# core/vol_surface.py
import numpy as np
import pandas as pd
import yfinance as yf
import scipy.optimize as opt
import scipy.interpolate as interp
from scipy.special import erf
import os
import warnings
warnings.filterwarnings('ignore')

class BlackScholes:
    @staticmethod
    def _ncdf(x):
        return 0.5 * (1.0 + erf(x / np.sqrt(2.0)))
    
    @staticmethod
    def call_price(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0:
            return max(S - K, 0.0)
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * BlackScholes._ncdf(d1) - K * np.exp(-r * T) * BlackScholes._ncdf(d2)
    
    @staticmethod
    def implied_volatility(price, S, K, T, r, option_type='call', tol=1e-6):
        if price <= 0 or T <= 0:
            return np.nan
        low, high = 1e-6, 5.0
        
        def objective(sigma):
            model_price = BlackScholes.call_price(S, K, T, r, sigma) if option_type == 'call' \
                         else BlackScholes.put_price(S, K, T, r, sigma)
            return model_price - price
        
        try:
            return opt.brentq(objective, low, high, xtol=tol)
        except ValueError:
            return np.nan

    @staticmethod
    def put_price(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0:
            return max(K - S, 0.0)
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return K * np.exp(-r * T) * BlackScholes._ncdf(-d2) - S * BlackScholes._ncdf(-d1)


class VolSurfaceCleaner:
    def __init__(self, ticker='SPY', risk_free_rate=0.045, days_min=7, days_max=180):
        self.ticker = ticker
        self.r = risk_free_rate
        self.days_min = days_min
        self.days_max = days_max
        self.raw_data = None
        self.cleaned_data = None
        self.iv_matrix = None
        self.expiries = None
        self.strikes = None
        self.interpolator = None

    def fetch_options_data(self):
        print(f"[1/4] Fetching options data for {self.ticker}...")
        try:
            stock = yf.Ticker(self.ticker)
            hist = stock.history(period="1d")
            if hist.empty:
                raise Exception("No price data")
            S = float(hist['Close'].iloc[-1])
            
            expirations = stock.options
            all_rows = []
            
            for exp in expirations:
                days = (pd.to_datetime(exp) - pd.Timestamp.today()).days
                if days < self.days_min or days > self.days_max:
                    continue
                try:
                    chain = stock.option_chain(exp)
                    for df_opt, typ in [(chain.calls, 'call'), (chain.puts, 'put')]:
                        df_opt = df_opt[['strike', 'bid', 'ask', 'volume']].copy()
                        df_opt['expiry'] = exp
                        df_opt['days'] = days
                        df_opt['T'] = days / 365.0
                        df_opt['type'] = typ
                        df_opt['underlying'] = S
                        df_opt['mid'] = (df_opt['bid'] + df_opt['ask']) / 2.0
                        all_rows.append(df_opt)
                except Exception:
                    continue
                    
            if not all_rows:
                raise Exception("No options retrieved")
            self.raw_data = pd.concat(all_rows, ignore_index=True)
            self.raw_data = self.raw_data[
                (self.raw_data['mid'] > 0) & 
                (self.raw_data['volume'] > 0) &
                (self.raw_data['strike'] > 0)
            ]
            print(f"✅ Fetched {len(self.raw_data)} records.")
        except Exception as e:
            print(f"⚠️ Failed to fetch real data ({e}). Using simulated data.")
            self._generate_simulated_data()

    def _generate_simulated_data(self):
        np.random.seed(42)
        S = 450.0
        strikes = np.linspace(400, 500, 25)
        expiries_days = np.array([15, 30, 45, 60, 90, 120, 180])
        data = []
        for days in expiries_days:
            T = days / 365.0
            for K in strikes:
                atm_iv = 0.22
                skew = -0.0004 * (K - S)
                term = 0.015 * np.sqrt(T)
                noise = np.random.normal(0, 0.008)
                iv_true = max(0.08, min(0.7, atm_iv + skew + term + noise))
                price = BlackScholes.call_price(S, K, T, self.r, iv_true)
                mid = price * (1 + np.random.normal(0, 0.005))
                data.append({
                    'strike': K, 'T': T, 'days': days,
                    'type': 'call', 'mid': mid, 'volume': 100,
                    'underlying': S, 'expiry': 'sim'
                })
        self.raw_data = pd.DataFrame(data)

    def compute_implied_volatility(self):
        print("[2/4] Computing implied volatility...")
        df = self.raw_data.copy()
        ivs = []
        for _, row in df.iterrows():
            iv = BlackScholes.implied_volatility(
                price=row['mid'], S=row['underlying'],
                K=row['strike'], T=row['T'], r=self.r,
                option_type=row['type']
            )
            ivs.append(iv)
        df['iv'] = ivs
        df = df.dropna(subset=['iv'])
        df = df[(df['iv'] > 0.01) & (df['iv'] < 3.0)]
        self.cleaned_data = df
        print(f"✅ Computed IV for {len(df)} options.")

    def clean_arbitrage_violations(self):
        print("[3/4] Cleaning arbitrage violations...")
        df = self.cleaned_data.copy()
        valid_rows = []
        for expiry in df['expiry'].unique():
            exp_df = df[df['expiry'] == expiry].sort_values('strike')
            if len(exp_df) < 3:
                valid_rows.append(exp_df)
                continue
            strikes = exp_df['strike'].values
            ivs = exp_df['iv'].values
            second_diff = np.diff(ivs, n=2)
            valid = np.ones(len(ivs), dtype=bool)
            for i in range(1, len(ivs)-1):
                if i-1 < len(second_diff) and second_diff[i-1] < -0.06:
                    valid[i] = False
            valid_rows.append(exp_df.iloc[valid])
        if valid_rows:
            self.cleaned_data = pd.concat(valid_rows, ignore_index=True)
        else:
            self.cleaned_data = pd.DataFrame()
        print(f"✅ After cleaning: {len(self.cleaned_data)} options remain.")

    def build_iv_surface(self):
        print("[4/4] Building IV surface...")
        df = self.cleaned_data
        if df.empty:
            raise ValueError("No data to build surface!")
        
        self.expiries = np.sort(df['T'].unique())
        self.strikes = np.sort(df['strike'].unique())
        IV_grid = np.full((len(self.expiries), len(self.strikes)), np.nan)
        
        for _, row in df.iterrows():
            i = np.argmin(np.abs(self.expiries - row['T']))
            j = np.argmin(np.abs(self.strikes - row['strike']))
            IV_grid[i, j] = row['iv']
        
        for i in range(len(self.expiries)):
            mask = ~np.isnan(IV_grid[i])
            if mask.sum() >= 2:
                f = interp.interp1d(self.strikes[mask], IV_grid[i][mask], 
                                    kind='linear', fill_value='extrapolate')
                IV_grid[i] = f(self.strikes)
        
        for j in range(len(self.strikes)):
            mask = ~np.isnan(IV_grid[:, j])
            if mask.sum() >= 2:
                f = interp.interp1d(self.expiries[mask], IV_grid[:, j][mask],
                                    kind='linear', fill_value='extrapolate')
                IV_grid[:, j] = f(self.expiries)
        
        self.iv_matrix = IV_grid
        self.interpolator = interp.RectBivariateSpline(
            self.expiries, self.strikes, IV_grid, kx=1, ky=1
        )
        print("✅ Volatility surface ready!")

    def save_surface(self, filepath):
        surf = self.get_surface_data()
        df_surface = pd.DataFrame(
            surf['iv_matrix'],
            index=np.round(surf['expiries'], 4),
            columns=np.round(surf['strikes'], 2)
        )
        df_surface.to_csv(filepath, float_format="%.4f")
        print(f"💾 Saved to {filepath}")

    def get_surface_data(self):
        return {
            'expiries': self.expiries,
            'strikes': self.strikes,
            'iv_matrix': self.iv_matrix
        }

    def run(self):
        self.fetch_options_data()
        self.compute_implied_volatility()
        self.clean_arbitrage_violations()
        self.build_iv_surface()
        return self