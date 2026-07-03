import os
import sys
import subprocess
from pathlib import Path

REAL_TRAFFIC_DIR = Path(__file__).parent
PROJECT_ROOT = REAL_TRAFFIC_DIR.parent
MAPS_DIR = PROJECT_ROOT / "maps"
NET_FILE = MAPS_DIR / "network.net.xml"

ROUTE_FILE = REAL_TRAFFIC_DIR / "real_routes.rou.xml"
STATS_DIR = REAL_TRAFFIC_DIR / "stats"
STATS_DIR.mkdir(exist_ok=True)

if not NET_FILE.exists():
    sys.exit("Не знайдено файл карти")

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
else:
    tools = r"C:\Users\GAMEMAX\Desktop\univer\SUMO\tools"
    os.environ['SUMO_HOME'] = r"C:\Users\GAMEMAX\Desktop\univer\SUMO"

random_trips_script = os.path.join(tools, "randomTrips.py")


cmd = [
    "python", random_trips_script,
    "-n", str(NET_FILE),
    "-r", str(ROUTE_FILE),
    "-e", "3600",
    "--period", "3.5",
    "--fringe-factor", "100",
    "--min-distance", "50",
    "--validate"
]

subprocess.call(cmd)

if ROUTE_FILE.exists():
    print("Файл маршрутів успішно створено")
else:
    print("Помилка генерації маршрутів")