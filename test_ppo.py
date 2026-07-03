import traci
from pathlib import Path
from stable_baselines3 import PPO

from traffic_env import SumoTrafficEnv

def main():
    print("Запуск тестування PPO")
    
    env = SumoTrafficEnv(gui=True)
    
    model_path = Path(__file__).parent / "stats" / "ppo_traffic_model"
    print(f"Завантаження моделі з {model_path}.zip")
    model = PPO.load(model_path)
    
    obs, _ = env.reset()
    
    total_spawned = 0
    total_arrived = 0
    total_wait_time = 0.0
    total_co2_mg = 0.0
    
    max_steps = 3600
    step_count = 0
        
    while step_count < max_steps:
        if step_count % 5 == 0:
            action, _ = model.predict(obs, deterministic=True)
            target_phase = 0 if action == 0 else 2
            traci.trafficlight.setPhase(env.unwrapped.tls_id, target_phase)
            
        traci.simulationStep()
        step_count += 1
        
        total_spawned += traci.simulation.getDepartedNumber()
        total_arrived += traci.simulation.getArrivedNumber()
        
        for edge in traci.edge.getIDList():
            if not edge.startswith(":"): 
                total_wait_time += traci.edge.getLastStepHaltingNumber(edge)
                total_co2_mg += traci.edge.getCO2Emission(edge)
                
        if step_count % 5 == 0:
            obs = env.unwrapped._get_obs()
            
    env.close()
    
    stuck = total_spawned - total_arrived
    avg_wait = (total_wait_time / total_spawned) if total_spawned > 0 else 0
    total_co2_kg = total_co2_mg / 1000000.0
    
    report = f"""
=========================================
ЗВІТ: ПРОФЕСІЙНИЙ ШІ 
=========================================
Кількість кроків (секунд): {max_steps}
Всього автомобілів з'явилося: {total_spawned}
Автомобілів успішно проїхали: {total_arrived}
Автомобілів застрягло в заторі: {stuck}

Середній час очікування 1 авто: {avg_wait:.1f} секунд
Загальні викиди CO2: {total_co2_kg:.2f} кг
=========================================
"""
    print(report)
    
    stats_dir = Path(__file__).parent / "stats"
    report_path = stats_dir / "ppo_report.txt"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()