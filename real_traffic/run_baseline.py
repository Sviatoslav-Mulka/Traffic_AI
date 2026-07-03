import os
import sys
import traci
from pathlib import Path

REAL_TRAFFIC_DIR = Path(__file__).parent
PROJECT_ROOT = REAL_TRAFFIC_DIR.parent
MAPS_DIR = PROJECT_ROOT / "maps"
STATS_DIR = REAL_TRAFFIC_DIR / "stats"

NET_FILE = MAPS_DIR / "network.net.xml"
ROUTE_FILE = REAL_TRAFFIC_DIR / "real_routes.rou.xml" 
STATS_FILE = STATS_DIR / "report_real_baseline.txt"

STATS_DIR.mkdir(exist_ok=True)

if not ROUTE_FILE.exists():
    sys.exit("Не знайдено real_routes.rou.xml")

if 'SUMO_HOME' not in os.environ:
    os.environ['SUMO_HOME'] = r"C:\Users\GAMEMAX\Desktop\univer\SUMO"
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

sumo_cmd = [
    "sumo-gui",
    "-n", str(NET_FILE),
    "-r", str(ROUTE_FILE),
    "--start",
    "--quit-on-end",
    "--emission-output", "dummy.xml", 
    "--device.emissions.probability", "1.0"
]

print("Стандартний світлофор")

vehicle_wait_times = {} 
total_co2_mg = 0.0      
vehicles_spawned = 0    
vehicles_finished = 0   
step = 0
max_steps = 3600 

try:
    traci.start(sumo_cmd)
    
    while step < max_steps:
        traci.simulationStep()
        
        vehicles_on_map = traci.vehicle.getIDList()
        
        for veh_id in vehicles_on_map:
            vehicle_wait_times[veh_id] = traci.vehicle.getAccumulatedWaitingTime(veh_id)
            total_co2_mg += traci.vehicle.getCO2Emission(veh_id)
        
        vehicles_spawned += traci.simulation.getDepartedNumber()
        vehicles_finished += traci.simulation.getArrivedNumber()

        if step % 100 == 0:
            print(f"Крок {step}/{max_steps} | Авто на карті: {len(vehicles_on_map)} | Доїхали: {vehicles_finished}")

        step += 1
    
except traci.FatalTraCIError:
    print("Симуляцію перервано")
finally:
    traci.close()

co2_kg = total_co2_mg / 1_000_000.0 

total_vehicles_seen = vehicles_spawned 

if total_vehicles_seen > 0:
    avg_waiting_time = sum(vehicle_wait_times.values()) / total_vehicles_seen
else:
    avg_waiting_time = 0.0

print("\nСимуляція завершена")

report_content = f"""
=========================================
ЗВІТ: СТАНДАРТНИЙ СВІТЛОФОР НА РЕАЛЬНОМУ ТРАФІКУ (Real Baseline)
=========================================
Кількість кроків (секунд): {step}
Всього автомобілів з'явилося: {total_vehicles_seen}
Автомобілів успішно проїхали: {vehicles_finished}
Автомобілів застрягло в заторі: {total_vehicles_seen - vehicles_finished}

Середній час очікування 1 авто: {avg_waiting_time:.1f} секунд
Загальні викиди CO2: {co2_kg:.2f} кг
=========================================
"""

with open(STATS_FILE, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Звіт збережено у: {STATS_FILE}")
print(report_content)