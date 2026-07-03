import os
import sys
import traci
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
MAPS_DIR = PROJECT_ROOT / "maps"
NET_FILE = MAPS_DIR / "network.net.xml"
ROUTE_FILE = MAPS_DIR / "routes.rou.xml"
VIEW_FILE = MAPS_DIR / "view.settings.xml" 


if not NET_FILE.exists():
    print(f"Не знайдено файл карти: {NET_FILE}")
    sys.exit(1)


view_content = """
<viewsettings>
    <scheme name="real world"/>
    <delay value="100"/>
</viewsettings>
"""
with open(VIEW_FILE, "w") as f:
    f.write(view_content)
print(f"Налаштування вигляду збережено в {VIEW_FILE}")


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    possible_path = r"C:\Users\GAMEMAX\Desktop\univer\SUMO\tools"
    if os.path.exists(possible_path):
        sys.path.append(possible_path)
        os.environ['SUMO_HOME'] = r"C:\Users\GAMEMAX\Desktop\univer\SUMO"
    else:
        sys.exit("Не знайдено SUMO_HOME. Перевір змінні середовища!")


print("Генерую потік авто")
random_trips_script = os.path.join(tools, "randomTrips.py")
random_trips_cmd = [
    "python", random_trips_script,
    "-n", str(NET_FILE),
    "-r", str(ROUTE_FILE),
    "-e", "3600",      
    "--period", "1.5", 
    "--fringe-factor", "100", 
    "--min-distance", "100",  
    "--validate"
]

try:
    subprocess.call(random_trips_cmd)
    print("Маршрути готові")
except Exception as e:
    print(f"Помилка генерації маршрутів {e}")
    sys.exit()


sumo_cmd = [
    "sumo-gui",
    "-n", str(NET_FILE),
    "-r", str(ROUTE_FILE),
    "-g", str(VIEW_FILE), 
    "--start",
    "--quit-on-end"
]

print("Запуск SUMO")
try:
    traci.start(sumo_cmd)
except Exception as e:
    print(f"Не вдалося запустити SUMO {e}")
    sys.exit()


step = 0
while step < 10000:
    try:
        traci.simulationStep()
        step += 1
    except traci.FatalTraCIError:
        print("Симуляцію зупинено")
        break

traci.close()