import os
from pathlib import Path
from stable_baselines3 import PPO

from traffic_env_ppo import SumoTrafficEnv 

def main():
    print("Запуск професійного ШІ")
    
    
    env = SumoTrafficEnv(gui=False)
    
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003)
    
    timesteps = 100000
    print(f"Навчання на {timesteps} кроків")
    
    model.learn(total_timesteps=timesteps)
    
    stats_dir = Path(__file__).parent / "stats"
    stats_dir.mkdir(exist_ok=True)
    model_save_path = stats_dir / "ppo_traffic_model"
    
    model.save(model_save_path)
    print(f"\nНавчання PPO завершено. Модель збережено у {model_save_path}.zip")
    
    env.close()

if __name__ == "__main__":
    main()