# plot_surface.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

def plot_volatility_surface(csv_path="volatility_surface.csv"):
    if not os.path.exists(csv_path):
        print(f"❌ Файл {csv_path} не найден. Сначала запустите vol_surface_cleaner.py")
        return

    # Загрузка данных
    df = pd.read_csv(csv_path, index_col=0)
    
    # Преобразуем индексы и колонки в числа
    T = df.index.astype(float).values      # время до экспирации (в годах)
    K = df.columns.astype(float).values    # страйки
    IV = df.values                         # матрица волатильности

    # Создаём сетку для 3D-графика
    K_grid, T_grid = np.meshgrid(K, T)

    # Построение графика
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(
        K_grid, T_grid, IV,
        cmap='viridis',
        edgecolor='none',
        alpha=0.9
    )
    
    ax.set_xlabel('Strike Price', fontsize=12)
    ax.set_ylabel('Time to Expiry (years)', fontsize=12)
    ax.set_zlabel('Implied Volatility', fontsize=12)
    ax.set_title('Volatility Surface (Arbitrage-Free)', fontsize=14)
    
    # Добавляем цветовую шкалу
    fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1)
    
    plt.tight_layout()
    plt.savefig("volatility_surface.png", dpi=200, bbox_inches='tight')
    print("✅ График сохранён как 'volatility_surface.png'")
    plt.show()

if __name__ == "__main__":
    plot_volatility_surface()