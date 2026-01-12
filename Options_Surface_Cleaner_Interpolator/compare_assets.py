# compare_assets.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from core.vol_surface import VolSurfaceCleaner

os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

# Генерация поверхностей
for ticker in ["SPY", "QQQ"]:
    print(f"\n--- Processing {ticker} ---")
    cleaner = VolSurfaceCleaner(ticker=ticker, risk_free_rate=0.045)
    cleaner.run()
    cleaner.save_surface(f"data/vol_surface_{ticker}.csv")

# Загрузка и сравнение ATM волатильности
fig, ax = plt.subplots(figsize=(10, 6))

for ticker in ["SPY", "QQQ"]:
    df = pd.read_csv(f"data/vol_surface_{ticker}.csv", index_col=0)
    T = df.index.astype(float)
    # Берём ATM: ближайший страйк к текущей цене (~450 для SPY, ~400 для QQQ)
    atm_col = df.columns[len(df.columns)//2]
    IV_atm = df[atm_col].values
    ax.plot(T, IV_atm, label=ticker, marker='o')

ax.set_xlabel("Time to Expiry (years)")
ax.set_ylabel("ATM Implied Volatility")
ax.set_title("Term Structure: SPY vs QQQ")
ax.legend()
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("plots/compare_SPY_QQQ.png", dpi=200)
plt.close()  # освобождает память
print("✅ Сравнение сохранено: plots/compare_SPY_QQQ.png")