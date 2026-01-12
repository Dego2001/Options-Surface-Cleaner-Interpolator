# Options Volatility Surface Cleaner & Interpolator

> A quantitative finance tool built by a 10th-grade student to construct arbitrage-free implied volatility surfaces from real market data.

This project fetches live options data, cleans noise and static arbitrage violations, and builds a smooth, interpolatable volatility surface — a core component in derivatives pricing used by hedge funds and investment banks.

## 🔍 Features

- ✅ **Real-time data** from Yahoo Finance (SPY, QQQ, and more)
- ✅ **Implied volatility calculation** via Black-Scholes inversion
- ✅ **Arbitrage cleaning**: removes violations of monotonicity and convexity
- ✅ **Surface interpolation** across strikes and expirations
- ✅ **Cross-asset comparison**: SPY vs QQQ term structure analysis
- ✅ **Multiple visualizations**:
  - Static plots (`PNG`)
  - Time-evolution animation (`GIF`)
  - Fully interactive 3D surface (`HTML` with Plotly)

## 📂 Project Structure
├── core/ # Core quant engine
│ ├── init.py
│ └── vol_surface.py # Black-Scholes, IV solver, cleaner
├── compare_assets.py # Compares SPY and QQQ volatility
├── animate_surface.py # Generates GIF of surface evolution
├── interactive_plot.py # Creates browser-based 3D plot
├── run_all.py # One-click pipeline execution
├── plots/ # Output visualizations
│ ├── compare_SPY_QQQ.png
│ ├── vol_surface_evolution.gif
│ └── vol_surface_interactive.html ← Open in browser!
└── requirements.txt # Dependencies

## ▶️ How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
2. Run the full pipeline:
bash
   python run_all.py
Explore results:
Open plots/vol_surface_interactive.html in your browser
View animation: plots/vol_surface_evolution.gif
Analyze CSV data in data/ (optional)
💡 No internet? The tool automatically falls back to realistic simulated data.

🎓 Academic Context
This project was developed as part of independent research into market microstructure and derivatives pricing. It demonstrates:

Understanding of option pricing theory (Black-Scholes, implied volatility)
Ability to implement arbitrage constraints (no butterfly arbitrage)
Proficiency in Python for quantitative finance (NumPy, SciPy, Pandas, Plotly)
Skills in data engineering and scientific visualization
Potential extensions include SVI parametrization, local volatility calibration, and integration with Russian market data (MOEX).

Built with curiosity • For students, by a student
```