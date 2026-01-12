# run_all.py (обновлённая версия)
import subprocess
import sys
import os

os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

scripts = [
    "compare_assets.py",
    "animate_surface.py",
    "interactive_plot.py"
]

for script in scripts:
    print(f"\n{'='*50}")
    print(f"🚀 Запуск: {script}")
    print('='*50)
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"❌ ОШИБКА при выполнении {script}!")
        break
    else:
        print(f"✅ {script} завершён успешно.")