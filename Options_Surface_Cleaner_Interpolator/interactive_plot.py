# interactive_plot.py
import os
import pandas as pd
import plotly.graph_objects as go
from core.vol_surface import VolSurfaceCleaner

os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

# Генерация данных
cleaner = VolSurfaceCleaner(ticker="SPY", risk_free_rate=0.045)
cleaner.run()
cleaner.save_surface("data/vol_surface_SPY.csv")

# Загрузка
df = pd.read_csv("data/vol_surface_SPY.csv", index_col=0)
T = df.index.astype(float).values
K = df.columns.astype(float).values
IV = df.values

# Plotly
fig = go.Figure(data=[go.Surface(
    x=K,
    y=T,
    z=IV,
    colorscale='Viridis',
    colorbar=dict(title="Implied Volatility")
)])

fig.update_layout(
    title="Interactive Volatility Surface (SPY)",
    scene=dict(
        xaxis_title='Strike Price',
        yaxis_title='Time to Expiry (years)',
        zaxis_title='Implied Volatility'
    ),
    width=800,
    height=600
)

fig.write_html("plots/vol_surface_interactive.html")
fig.show()
print("✅ Интерактивный график: plots/vol_surface_interactive.html")