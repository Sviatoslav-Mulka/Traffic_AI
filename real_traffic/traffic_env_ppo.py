import os
import sys
import traci
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from pathlib import Path

class SumoTrafficEnv(gym.Env):

    def __init__(self, gui=False):
        super(SumoTrafficEnv, self).__init__()
        
        self.proj_root = Path(__file__).parent
        self.net_file = self.proj_root / "network.net.xml"
        self.route_file = self.proj_root / "real_routes.rou.xml"
        
        if 'SUMO_HOME' not in os.environ:
            os.environ['SUMO_HOME'] = r"C:\Users\GAMEMAX\Desktop\univer\SUMO"
            sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
            
        self.sumo_binary = "sumo-gui" if gui else "sumo"
        self.sumo_cmd = [
            self.sumo_binary, "-n", str(self.net_file), "-r", str(self.route_file),
            "--waiting-time-memory", "10000", "--no-step-log", "true",
            "--no-warnings", "true", "--start", "true", "--quit-on-end", "true"
        ]
        
        self.action_space = spaces.Discrete(2) 
        
        
        self.observation_space = spaces.Box(
            low=0, high=100, shape=(6,), dtype=np.float32
        )
        
        self.tls_id = None
        self.incoming_lanes = []
        self.step_count = 0
        self.max_steps = 3600
        self.sumo_running = False
        self.delta_time = 5 
        
        self.last_action = None
        self.time_since_switch = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if self.sumo_running:
            traci.close()
        
        traci.start(self.sumo_cmd)
        self.sumo_running = True
        self.step_count = 0
        self.last_action = 0 
        self.time_since_switch = 0.0 
        
        if self.tls_id is None:
            tls_list = traci.trafficlight.getIDList()
            if len(tls_list) == 0:
                raise ValueError("Світлофор не знайдено")
            self.tls_id = tls_list[0]
            self.incoming_lanes = list(set(traci.trafficlight.getControlledLanes(self.tls_id)))

        return self._get_obs(), {}

    def step(self, action):
        target_phase = 0 if action == 0 else 2
        
        switching_penalty = 0
        if self.last_action is not None and action != self.last_action:
            switching_penalty = -1.0 
            self.time_since_switch = 0.0 
        else:
            self.time_since_switch += self.delta_time 
            
        self.last_action = action
        traci.trafficlight.setPhase(self.tls_id, target_phase)
        
        for _ in range(self.delta_time):
            traci.simulationStep()
            self.step_count += 1
            if self.step_count >= self.max_steps:
                break
                
        obs = self._get_obs()
        reward = self._get_reward() + switching_penalty
        
        terminated = self.step_count >= self.max_steps
        truncated = False
        
        return obs, reward, terminated, truncated, {}

    def _get_obs(self):
        obs = []
        for lane in self.incoming_lanes:
            obs.append(traci.lane.getLastStepHaltingNumber(lane))
            
        current_phase = traci.trafficlight.getPhase(self.tls_id)
        is_phase_0 = 1.0 if current_phase == 0 else 0.0
        is_phase_2 = 1.0 if current_phase == 2 else 0.0
        
        timer_norm = self.time_since_switch / 100.0 
        
        obs.extend([is_phase_0, is_phase_2, timer_norm])
        return np.array(obs, dtype=np.float32)

    def _get_reward(self):
        total_wait = 0.0
        for lane in self.incoming_lanes:
            total_wait += traci.lane.getWaitingTime(lane)
        return -total_wait 

    def close(self):
        if self.sumo_running:
            traci.close()
            self.sumo_running = False