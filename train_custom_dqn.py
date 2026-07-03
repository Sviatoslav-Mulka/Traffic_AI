import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque
import os
import csv
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

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        state, action, reward, next_state, done = zip(*random.sample(self.buffer, batch_size))
        return np.array(state), action, reward, np.array(next_state), done

    def __len__(self):
        return len(self.buffer)

class TrafficAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        self.gamma = 0.99          
        self.epsilon = 1.0         
        self.epsilon_min = 0.05    
        self.epsilon_decay = 0.995 
        self.learning_rate = 0.0001
        self.batch_size = 128

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = DQN(state_size, action_size).to(self.device)
        self.target_model = DQN(state_size, action_size).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.memory = ReplayBuffer(100000)

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.model(state)
        return torch.argmax(q_values).item()

    def train(self):
        if len(self.memory) < self.batch_size:
            return None

        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        current_q = self.model(states).gather(1, actions)
        next_q = self.target_model(next_states).max(1)[0].unsqueeze(1)
        expected_q = rewards + (self.gamma * next_q * (1 - dones))

        loss = F.mse_loss(current_q, expected_q.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def update_target_network(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def main():
    print("Запуск оптимізованої DQN")
    env = SumoTrafficEnv(gui=False) 
    
    obs, _ = env.reset()
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    
    agent = TrafficAgent(state_size, action_size)
    episodes = 1000 
    
    stats_dir = Path(__file__).parent / "stats"
    stats_dir.mkdir(exist_ok=True)
    model_save_path = stats_dir / "custom_dqn_model.pth"
    csv_file_path = stats_dir / "training_history_final.csv" 

    best_reward = float('-inf')
    
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Episode", "Total_Reward", "Epsilon", "Average_Loss"])

    for e in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        losses = []
        
        while not done:
            action = agent.act(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            agent.memory.push(state, action, reward, next_state, done)
            loss = agent.train()
            
            if loss is not None:
                losses.append(loss)
            
            state = next_state
            total_reward += reward
            
        agent.decay_epsilon()
        
        if e % 5 == 0:
            agent.update_target_network()
            
        avg_loss = np.mean(losses) if losses else 0.0
        
        print(f"Епізод: {e+1}/{episodes} | Штраф: {total_reward:.1f} | Epsilon: {agent.epsilon:.2f} | Loss: {avg_loss:.2f}")
        
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([e+1, total_reward, agent.epsilon, avg_loss])
        
        if total_reward > best_reward:
            best_reward = total_reward
            torch.save(agent.model.state_dict(), model_save_path)
            print("Знайдено кращу стратегію. Модель збережено")

    env.close()
    print(f"\nФінальне навчання завершено")

if __name__ == "__main__":
    main()