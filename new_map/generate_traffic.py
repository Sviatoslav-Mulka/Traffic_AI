import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
MAPS_DIR = PROJECT_ROOT

NET_FILE = MAPS_DIR / "new_network.net.xml" 
ROUTE_FILE = MAPS_DIR / "new_golden_routes.rou.xml" 

print(f"Пошук {NET_FILE}")
if not NET_FILE.exists():
    sys.exit("Карти не знайдено")

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
else:
    tools = r"C:\Users\GAMEMAX\Desktop\univer\SUMO\tools"
    os.environ['SUMO_HOME'] = r"C:\Users\GAMEMAX\Desktop\univer\SUMO"

if not os.path.exists(tools):
    sys.exit("Папку tools не знайдено в SUMO_HOME")

random_trips_script = os.path.join(tools, "randomTrips.py")

cmd = [
    "python", random_trips_script,
    "-n", str(NET_FILE),
    "-r", str(ROUTE_FILE),
    "-e", "3600",             # симуляція на 1 годину 
    "--period", "3.5",        # авто в середньому кожні 3.5 с 
    "--fringe-factor", "100", # тільки з країв карти
    "--min-distance", "50",   # щоб їхали через центр
    "--validate"              
]

print("Генерація трафіку для нової мапи")
try:
    subprocess.call(cmd)
    print(f"Файл з маршрутами збережено: {ROUTE_FILE}")
except Exception as e:
    print(f"Помилка {e}")