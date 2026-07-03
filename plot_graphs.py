import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    
    csv_file = Path(__file__).parent / "stats" / "training_history_final.csv"
    
    if not csv_file.exists():
        print(f"Файл {csv_file} не знайдено")
        return

    data = pd.read_csv(csv_file)

    plt.figure(figsize=(10, 5))
    
    plt.plot(data['Episode'], data['Total_Reward'], label='Штраф за епізод', color='blue', marker='o', markersize=3)
    
    plt.title('Процес навчання власної нейромережі (DQN)')
    plt.xlabel('Епізод навчання')
    plt.ylabel('Сумарна нагорода')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    save_path = Path(__file__).parent / "stats" / "dqn_learning_curve.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Графік збережено у {save_path}")
    
    plt.show()

if __name__ == "__main__":
    main()