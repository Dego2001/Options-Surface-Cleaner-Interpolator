# animate_surface.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from core.vol_surface import VolSurfaceCleaner

os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

# Генерация данных (один раз)
cleaner = VolSurfaceCleaner(ticker="SPY", risk_free_rate=0.045)
cleaner.run()
cleaner.save_surface("data/vol_surface_SPY.csv")

# Загрузка
df = pd.read_csv("data/vol_surface_SPY.csv", index_col=0)
T = df.index.astype(float).values
K = df.columns.astype(float).values
IV = df.values

# Подготовка к анимации
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

def update(frame):
    ax.clear()
    current_iv = IV[:frame+1] if frame < len(IV) else IV
    current_T = T[:frame+1] if frame < len(T) else T
    K_grid, T_grid = np.meshgrid(K, current_T)
    ax.plot_surface(K_grid, T_grid, current_iv, cmap='viridis', edgecolor='none')
    ax.set_xlabel('Strike')
    ax.set_ylabel('Time to Expiry')
    ax.set_zlabel('IV')
    ax.set_title(f'Volatility Surface (Frame {frame+1}/{len(T)})')

ani = FuncAnimation(fig, update, frames=len(T), repeat=False, interval=1000)
ani.save("plots/vol_surface_evolution.gif", writer='pillow', fps=1)
plt.close()  # освобождает память
print("✅ Анимация сохранена: plots/vol_surface_evolution.gif")