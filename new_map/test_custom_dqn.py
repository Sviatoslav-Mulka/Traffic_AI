import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import traci
from pathlib import Path


from traffic_env import SumoTrafficEnv


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

def test_model():
    print("Запуск тестування моделі Custom DQN")
    
    
    stats_dir = Path(__file__).parent / "stats"
    model_path = stats_dir / "custom_dqn_model.pth"
    report_path = stats_dir / "report_custom_dqn.txt"
    
    if not model_path.exists():
        print(f"Помилка: Модель не знайдено за шляхом {model_path}")
        return

    
    env = SumoTrafficEnv(gui=True)
    obs, _ = env.reset()
    
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DQN(state_size, action_size).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval() 
    print("Модель успішно завантажена")

    
    vehicle_wait_times = {}
    total_co2_mg = 0.0
    vehicles_spawned = 0
    vehicles_finished = 0
    
    total_reward = 0
    done = False
    
    
    while not done:
        
        state_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device)
        with torch.no_grad():
            q_values = model(state_tensor)
        action = torch.argmax(q_values).item()
        
        
        target_phase = 0 if action == 0 else 2
        traci.trafficlight.setPhase(env.tls_id, target_phase)
        
        step_reward = 0
        for _ in range(env.delta_time):
            if env.step_count >= env.max_steps:
                break
                
            traci.simulationStep()
            env.step_count += 1
            
            
            vehicles_on_map = traci.vehicle.getIDList()
            for veh_id in vehicles_on_map:
                vehicle_wait_times[veh_id] = traci.vehicle.getAccumulatedWaitingTime(veh_id)
                total_co2_mg += traci.vehicle.getCO2Emission(veh_id)
                
            vehicles_spawned += traci.simulation.getDepartedNumber()
            vehicles_finished += traci.simulation.getArrivedNumber()
            
            
            if env.step_count % 100 == 0:
                print(f"Крок {env.step_count}/{env.max_steps} | Авто: {len(vehicles_on_map)} | Фаза: {target_phase}")

        
        obs = env._get_obs()
        reward = env._get_reward()
        total_reward += reward
        
        done = env.step_count >= env.max_steps

    env.close()
    
    
    co2_kg = total_co2_mg / 1_000_000.0
    total_vehicles_seen = vehicles_spawned
    
    if total_vehicles_seen > 0:
        avg_waiting_time = sum(vehicle_wait_times.values()) / total_vehicles_seen
    else:
        avg_waiting_time = 0.0

    print("\nТестування завершено")

    report_content = f"""
=========================================
ЗВІТ: ВЛАСНА НЕЙРОМЕРЕЖА (Custom DQN)
=========================================
Епізодів навчання пройдено: 1000
Кількість кроків (секунд): {env.step_count}
Всього автомобілів з'явилося: {total_vehicles_seen}
Автомобілів успішно проїхали: {vehicles_finished}
Автомобілів застрягло в заторі: {total_vehicles_seen - vehicles_finished}

Середній час очікування 1 авто: {avg_waiting_time:.1f} секунд
Загальні викиди CO2: {co2_kg:.2f} кг
=========================================
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Звіт збережено у {report_path}")
    print(report_content)

if __name__ == "__main__":
    test_model()