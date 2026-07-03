# 🚦 Adaptive Traffic Light Control via Reinforcement Learning
### *B.Sc. Thesis — Lviv Ivan Franko National University, 2026*

> Оптимізація керування світлофором на модельованому перехресті засобами навчання з підкріпленням  
> Optimization of Traffic Light Control at a Simulated Intersection Using Reinforcement Learning
---

## 🌐 Language / Мова

- [🇬🇧 English version](#-english)
- [🇺🇦 Українська версія](#-українська)

---

# 🇬🇧 English

## 📌 Problem Statement

Urban infrastructure worldwide is under increasing pressure from growing vehicle numbers. Traditional traffic light systems operate on **fixed timers** — switching phases at predetermined intervals regardless of actual queue lengths on the road. This results in:

- 🔴 Unnecessary waiting time when adjacent lanes are empty ("empty intersection" problem)
- 💨 Increased CO₂ emissions due to constant stop-and-go cycles
- 🐢 Reduced intersection throughput during asymmetric traffic loads
- 🔁 No adaptation to real-time road conditions

This project addresses these limitations by replacing static timers with **Reinforcement Learning agents** that observe the intersection state in real time and decide autonomously when to switch signal phases.

---

## 🧠 Scientific Approach

The task is formalized as a **Markov Decision Process (MDP)** — the mathematical foundation for Reinforcement Learning:

| MDP Component | Description |
|---|---|
| **State Space (S)** | Normalized queue lengths per lane + current active phase index + seconds since last phase switch |
| **Action Space (A)** | Binary: `0` — keep current phase, `1` — switch to next phase |
| **Reward Function (R)** | Negative penalty for total halted vehicles + switching penalty (−1.0 per phase change) |
| **Discount Factor (γ)** | Balances immediate vs. future reward |

The **hybrid reward function** is key: the agent is penalized for queues AND for switching too frequently. This prevents "traffic light flickering" — forcing the network to hold a green phase long enough for vehicle groups to clear.

### Implemented Algorithms

#### 🔷 Custom Deep Q-Network (DQN)
Built from scratch using **PyTorch**. Architecture:
- Input layer (6 neurons) → Hidden layer (64) → Hidden layer (64) → Output (2 Q-values)
- Activation: ReLU
- Optimizer: Adam (lr = 0.0001)
- Replay Buffer: 100,000 transitions
- Target Network update: every N steps
- ε-greedy exploration with decay = 0.995

#### 🔶 Proximal Policy Optimization (PPO)
Industrial-grade implementation via **Stable Baselines3**. Actor-Critic architecture:
- **Actor**: neural network that proposes actions (controls the traffic light)
- **Critic**: neural network that evaluates state value V(s)
- Clipped objective function prevents catastrophic policy updates

---

## 🛠️ Technology Stack

| Tool | Version | Role |
|---|---|---|
| **Python** | 3.10+ | Core language & integration platform |
| **SUMO** | Latest | Microscopic traffic simulation |
| **TraCI** | — | TCP/IP client-server interface (Python ↔ SUMO) |
| **Gymnasium** | Latest | Standard RL environment wrapper (OpenAI Gym successor) |
| **PyTorch** | 2.x | Custom DQN neural network implementation |
| **Stable Baselines3** | Latest | Production-ready PPO algorithm |
| **Pandas** | Latest | Data collection and statistical analysis |
| **Matplotlib** | Latest | Result visualization and training curves |

---

## 📊 Experimental Results

Three testing scenarios were conducted, each lasting **3600 seconds** (1 simulated hour).

### Scenario 1 — Stress Test (Maximum Load, ~1 vehicle/second)

| Metric | Static Timer | Custom DQN | PPO |
|---|---|---|---|
| Total vehicles generated | 1612 | 1426 | 1803 |
| Vehicles passed successfully | 1440 | 1252 | **1640** |
| Vehicles stuck in jam | 172 | 174 | **163** |
| Avg. wait time per vehicle (s) | **30** | 218 | 118 |
| Total CO₂ emissions (kg) | 950 | 934 | **873** |

> ⚠️ Under extreme saturation, static timers achieve lower wait times due to their uniform switching — however this comes at the cost of higher emissions. PPO achieved the highest throughput (+14%) and lowest CO₂.

---

### Scenario 2 — Realistic Urban Load (~1000 vehicles/hour, 50% capacity)

| Metric | Static Timer | Custom DQN | PPO |
|---|---|---|---|
| Total vehicles | 1029 | 1029 | 1029 |
| Vehicles passed successfully | 991 | **1008** | **1008** |
| Vehicles stuck in jam | 38 | **21** | **21** |
| Avg. wait time per vehicle (s) | 16 | **7** | 10 |
| Total CO₂ emissions (kg) | 210 | 184 | **177** |

> ✅ Under realistic conditions both AI models outperformed the static baseline across all metrics. **DQN reduced average waiting time by 56%**, while **PPO cut CO₂ emissions by 15.7%**.

---

### Scenario 3 — Generalization Test (Different Intersection Topology)

Both models were deployed on a **completely different intersection geometry** (residential road joining a main road) **without any retraining** — using only previously acquired knowledge.

| Metric | Static Timer | Custom DQN | PPO |
|---|---|---|---|
| Total vehicles | 985 | 1029 | 1029 |
| Vehicles passed successfully | 948 | **1017** | **1017** |
| Vehicles stuck in jam | 37 | **12** | **12** |
| Avg. wait time per vehicle (s) | 23 | **1** | **2** |
| Total CO₂ emissions (kg) | 234 | 123 | **115** |

> 🌟 CO₂ emissions dropped by **more than 2×**. Both agents generalized successfully — proving they learned a general adaptive traffic control strategy, not just memorized a specific intersection map.

---

## 🔍 Key Scientific Findings

### 🔁 Policy Degradation Phenomenon
A critical finding during DQN training: the model trained for 100 episodes (avg. wait = 126s) outperformed the one trained for 1000 episodes (avg. wait = 218s). This is a classic manifestation of **Q-value overestimation** — the network overfits to local traffic patterns and loses generalization ability. This validates the necessity of **early stopping** and careful hyperparameter tuning.

### ♻️ The CO₂ Paradox
An unexpected non-linear relationship was discovered between wait time and emissions. The static timer, despite having the lowest average wait time in stress tests, generated the **most CO₂**. This is because peak emissions occur not during idle waiting, but during **acceleration cycles**. Static timers artificially break traffic flow every 30 seconds, forcing large vehicle groups to constantly stop and restart. AI models form **continuous flow policies** — sacrificing some vehicles on secondary lanes to let the main flow pass without stopping.

### 🧩 The "Empty Intersection" Problem
Custom DQN eliminated this critical inefficiency: unlike a static timer, the AI reads virtual sensor data and immediately switches the phase when a perpendicular lane is empty — eliminating wasted green time.

---

## 📈 Training Dynamics (DQN)

- **Episodes 1–100**: High randomness (ε ≈ 1.0), penalties reach −25,000 per episode
- **Episodes 100–400**: Replay buffer fills with critical states; network begins learning patterns
- **Episodes 400–1000**: Reward curve shows stable upward trend, stabilizing in upper range
- **Best checkpoint**: Episode ~100 (before Q-value overestimation sets in)

---

## 🗂️ Project Structure

```
Traffic_AI/
│
├── traffic_env.py              # Custom Gymnasium environment (TraCI interface) for DQN
├── traffic_env_ppo.py          # Adapted environment for Stable Baselines3 / PPO
│
├── train_custom_dqn.py         # DQN training script (PyTorch, from scratch)
├── train_ppo.py                # PPO training script (Stable Baselines3)
│
├── test_custom_dqn.py          # Deterministic evaluation of trained DQN model
├── test_ppo.py                 # Deterministic evaluation of trained PPO model
├── run_baseline.py             # Static timer baseline test
├── test_map.py                 # Generalization test on alternative intersection topology
│
├── generate_traffic.py         # XML traffic flow generator (stress test scenario)
│
├── plot_graphs.py              # Training curve visualization
├── plot_comparison.py          # Side-by-side comparison charts
│
├── stats/                      # Reports & trained models (stress test scenario)
│   ├── training_history_final.csv   # Full DQN training history (1000 episodes)
│   ├── report_baseline.txt          # Static timer test report
│   ├── report_custom_dqn.txt        # Custom DQN evaluation report
│   └── ppo_report.txt               # PPO evaluation report
│
├── real_traffic/               # Realistic urban load scenario (~1000 vehicles/hour)
│   ├── generate_real_traffic.py     # Traffic generator for realistic scenario
│   ├── traffic_env.py               # Environment configured for realistic flow
│   ├── stats/                       # Reports for realistic scenario
│   └── ...
│
├── new_map/                    # Generalization test — alternative intersection
│   ├── stats/                       # Reports for new topology
│   └── ...
│
├── maps/                       # SUMO network files (.net.xml, .rou.xml, .sumocfg)
│
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

1. **Install SUMO** (Simulation of Urban MObility):
   - Download from: [https://eclipse.dev/sumo/](https://eclipse.dev/sumo/)
   - Make sure `sumo` and `sumo-gui` are accessible from PATH

2. **Python 3.10+**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Traffic_AI.git
cd Traffic_AI

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Install Python dependencies
pip install -r requirements.txt
```

### ⚠️ Important: Configure SUMO Path

Before running any script, open the following files and **replace the SUMO path** with your local installation path:

- `generate_traffic.py`
- `run_baseline.py`
- `traffic_env.py`
- `traffic_env_ppo.py`
- `test_map.py`
- `real_traffic/generate_real_traffic.py`

Look for a line similar to:
```python
sumoCmd = ["C:/path/to/sumo-win64/bin/sumo", "-c", "maps/intersection.sumocfg"]
```
Replace `"C:/path/to/sumo-win64/bin/sumo"` with your actual SUMO binary path.

### Running

```bash
# --- Stress Test Scenario (Maximum Load) ---

# Generate traffic file
python generate_traffic.py

# Test the static timer baseline
python run_baseline.py

# Train the custom DQN agent (1000 episodes)
python train_custom_dqn.py

# Train the PPO agent
python train_ppo.py

# Evaluate trained models (deterministic mode)
python test_custom_dqn.py
python test_ppo.py

# --- Realistic Traffic Scenario ---
cd real_traffic
python generate_real_traffic.py
python run_baseline.py
python test_custom_dqn.py
python test_ppo.py

# --- Generalization Test (New Intersection) ---
cd ../new_map
python test_map.py

# --- Visualize Results ---
python plot_graphs.py        # DQN training curve
python plot_comparison.py   # Comparative bar charts
```

> 💡 All test results and trained model weights are saved in the `stats/` folders of each scenario directory.

---

## 📦 Full Project Archive (Google Drive)

The full project archive (including trained model weights, generated traffic files, SUMO configs, and all test reports) is available for download:

> 🔗 **[Download Full Archive from Google Drive](https://drive.google.com/file/d/14Jmm2hFji4Ab4dL-Yhkvn-v8QID5h6vG/view?usp=sharing)**

---

## 🔭 Future Work

- **Multi-intersection coordination** — green wave synchronization across multiple consecutive signals
- **Public transport priority** — dedicated phase logic for buses and trams
- **Pedestrian flow integration** — dynamic pedestrian crossing phase management
- **Computer vision input** — replacing simulated queue sensors with real camera feeds
- **Multi-agent RL** — cooperative control across a network of intersections
- **Auto-adaptive architecture** — a model that automatically adjusts to any intersection topology

---

# 🇺🇦 Українська

## 📌 Постановка задачі

Традиційні системи керування дорожнім рухом, побудовані на основі **статичних таймерів**, виявляються неефективними в умовах динамічної зміни транспортних потоків. Це призводить до:

- 🔴 Зайвого часу очікування, коли сусідня смуга порожня ("проблема порожнього перехрестя")
- 💨 Збільшення викидів CO₂ через постійні цикли зупинок та розгону
- 🐢 Зниження пропускної здатності при нерівномірних транспортних потоках
- 🔁 Відсутності адаптації до реальних умов руху в реальному часі

Цей проєкт вирішує ці проблеми, замінюючи статичні таймери **агентами навчання з підкріпленням**, які спостерігають за станом перехрестя в реальному часі та самостійно приймають рішення щодо переключення фаз.

---

## 🧠 Наукова основа

Задача формалізована як **Марківський процес прийняття рішень (MDP)**:

| Компонент MDP | Опис |
|---|---|
| **Простір станів (S)** | Нормалізована кількість зупинених авто на кожній смузі + поточна фаза + секунди після останнього переключення |
| **Простір дій (A)** | Бінарний: `0` — утримати поточну фазу, `1` — переключити на наступну |
| **Функція винагороди (R)** | Від'ємний штраф за зупинені авто + штраф за переключення (−1.0 за кожну зміну фази) |
| **Коефіцієнт дисконтування (γ)** | Баланс між миттєвою та майбутньою винагородою |

### Реалізовані алгоритми

#### 🔷 Власна Deep Q-Network (DQN)
Реалізована з нуля на **PyTorch**:
- Архітектура MLP: Input(6) → Dense(64) → Dense(64) → Output(2)
- Активація: ReLU, оптимізатор: Adam (lr = 0.0001)
- Replay Buffer: 100 000 переходів, згасання ε = 0.995

#### 🔶 Proximal Policy Optimization (PPO)
Промисловий алгоритм через **Stable Baselines3**:
- Архітектура Актор-Критик
- Обмежена цільова функція запобігає катастрофічним оновленням політики

---

## 🛠️ Технологічний стек

| Інструмент | Роль |
|---|---|
| **Python 3.10+** | Основна мова та платформа інтеграції |
| **SUMO** | Мікроскопічний симулятор дорожнього руху |
| **TraCI** | TCP/IP інтерфейс (Python ↔ SUMO) |
| **Gymnasium** | Стандартна обгортка RL-середовища |
| **PyTorch** | Реалізація власної нейромережі DQN |
| **Stable Baselines3** | Промислова реалізація алгоритму PPO |
| **Pandas / Matplotlib** | Збір та візуалізація статистики |

---

## 📊 Результати експериментів

### Сценарій 1 — Стрес-тест (максимальне навантаження)

| Метрика | Статичний таймер | Власна DQN | PPO |
|---|---|---|---|
| Всього згенеровано авто | 1612 | 1426 | 1803 |
| Успішно проїхали | 1440 | 1252 | **1640** |
| Застрягли у заторі | 172 | 174 | **163** |
| Середній час очікування (с) | **30** | 218 | 118 |
| Загальні викиди CO₂ (кг) | 950 | 934 | **873** |

### Сценарій 2 — Реалістичне міське навантаження (~1000 авт/год)

| Метрика | Статичний таймер | Власна DQN | PPO |
|---|---|---|---|
| Всього авто | 1029 | 1029 | 1029 |
| Успішно проїхали | 991 | **1008** | **1008** |
| Застрягли у заторі | 38 | **21** | **21** |
| Середній час очікування (с) | 16 | **7** | 10 |
| Загальні викиди CO₂ (кг) | 210 | 184 | **177** |

> ✅ **DQN знизила середній час очікування на 56%.** PPO скоротила викиди CO₂ на **15.7%** порівняно зі статичним таймером.

### Сценарій 3 — Тест на іншій топології (без перенавчання)

| Метрика | Статичний таймер | Власна DQN | PPO |
|---|---|---|---|
| Всього авто | 985 | 1029 | 1029 |
| Успішно проїхали | 948 | **1017** | **1017** |
| Застрягли у заторі | 37 | **12** | **12** |
| Середній час очікування (с) | 23 | **1** | **2** |
| Загальні викиди CO₂ (кг) | 234 | 123 | **115** |

> 🌟 Викиди CO₂ знизилися більш ніж **вдвічі**. Обидві моделі успішно узагальнили навчений досвід на нову топологію без додаткового тренування.

---

## 🔍 Ключові наукові висновки

### 🔁 Феномен деградації політики
Модель, навчена 100 епізодів (середній час = 126 с), перевершила модель, навчену 1000 епізодів (218 с). Це класичний прояв **переоцінки Q-значень** — необхідність ранньої зупинки та тонкого налаштування гіперпараметрів підтверджена експериментально.

### ♻️ CO₂ парадокс
Статичний таймер, маючи найменший середній час очікування при стрес-тесті, згенерував **найбільше CO₂**. Пікові викиди відбуваються під час розгону, а не простою. Штучні перемикання кожні 30 секунд змушують великі групи авто постійно зупинятися та розганятися. AI-агенти формують **політику безперервного потоку**, економлячи паливо.

### 🧩 Проблема порожнього перехрестя
Власна DQN усунула цю ключову неефективність: на відміну від таймера, ШІ зчитує дані сенсорів і миттєво переключає фазу, якщо перпендикулярна смуга порожня.

---

## 🚀 Швидкий старт

### Вимоги

1. **Встановити SUMO**: [https://eclipse.dev/sumo/](https://eclipse.dev/sumo/)
2. **Python 3.10+**

### Встановлення

```bash
# 1. Клонувати репозиторій
git clone https://github.com/YOUR_USERNAME/Traffic_AI.git
cd Traffic_AI

# 2. Встановити залежності
pip install -r requirements.txt
```

### ⚠️ Важливо: налаштування шляху SUMO

У наступних файлах потрібно **замінити шлях до SUMO** на власний:
`generate_traffic.py`, `run_baseline.py`, `traffic_env.py`, `traffic_env_ppo.py`, `test_map.py`, `real_traffic/generate_real_traffic.py`

```python
# Знайти рядок типу:
sumoCmd = ["C:/path/to/sumo-win64/bin/sumo", "-c", "maps/intersection.sumocfg"]
# Замінити шлях на власний
```

### Запуск

```bash
# Стрес-тест сценарій
python generate_traffic.py      # Генерація трафіку
python run_baseline.py          # Тест статичного таймера
python train_custom_dqn.py      # Навчання DQN (1000 епізодів)
python train_ppo.py             # Навчання PPO
python test_custom_dqn.py       # Оцінка DQN
python test_ppo.py              # Оцінка PPO

# Реалістичний сценарій
cd real_traffic && python generate_real_traffic.py

# Тест на новій топології
cd ../new_map && python test_map.py

# Побудова графіків
python plot_graphs.py           # Крива навчання DQN
python plot_comparison.py       # Порівняльні діаграми
```

---

## 📦 Повний архів проєкту (Google Drive)

Повний архів проєкту (навчені моделі, файли трафіку, конфіги SUMO та всі звіти) доступний для завантаження:

> 🔗 **[Завантажити повний архів з Google Drive](https://drive.google.com/file/d/14Jmm2hFji4Ab4dL-Yhkvn-v8QID5h6vG/view?usp=sharing)**

---

## 🗂️ Структура проєкту

```
Traffic_AI/
│
├── traffic_env.py              # Gymnasium-середовище (TraCI інтерфейс) для DQN
├── traffic_env_ppo.py          # Адаптоване середовище для PPO / Stable Baselines3
│
├── train_custom_dqn.py         # Навчання DQN (PyTorch, з нуля)
├── train_ppo.py                # Навчання PPO (Stable Baselines3)
│
├── test_custom_dqn.py          # Детермінована оцінка моделі DQN
├── test_ppo.py                 # Детермінована оцінка моделі PPO
├── run_baseline.py             # Тест базового статичного таймера
├── test_map.py                 # Тест на новій топології перехрестя
│
├── generate_traffic.py         # Генератор XML файлів трафіку (стрес-сценарій)
├── plot_graphs.py              # Крива навчання DQN
├── plot_comparison.py          # Порівняльні діаграми
│
├── stats/                      # Звіти та навчені моделі (стрес-сценарій)
│   ├── training_history_final.csv   # Повна історія навчання DQN (1000 епізодів)
│   ├── report_baseline.txt          # Звіт статичного таймера
│   ├── report_custom_dqn.txt        # Звіт кастомної DQN
│   └── ppo_report.txt               # Звіт PPO
│
├── real_traffic/               # Реалістичне навантаження (~1000 авт/год)
│   ├── generate_real_traffic.py
│   ├── stats/
│   └── ...
│
├── new_map/                    # Нова топологія — тест генералізації
│   ├── stats/
│   └── ...
│
├── maps/                       # SUMO мережеві файли (.net.xml, .rou.xml, .sumocfg)
└── requirements.txt
```

---

## 🔭 Напрями подальшої роботи

- **Координація кількох перехресть** — синхронізація "зеленої хвилі"
- **Пріоритет громадського транспорту** — окрема логіка фаз для автобусів і трамваїв
- **Інтеграція пішохідних потоків** — динамічне керування пішохідними переходами
- **Вхід з комп'ютерного зору** — заміна симульованих сенсорів реальними камерами
- **Мультиагентне RL** — кооперативне керування мережею перехресть
- **Авто-адаптивна архітектура** — модель, що автоматично підлаштовується під будь-яку топологію

---

