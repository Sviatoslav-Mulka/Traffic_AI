import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def main():

    labels = ['Статичний таймер', 'Власна DQN', 'Професійна PPO']
    wait_times = [30, 218, 118] 
    co2_emissions = [950, 934, 873] 
    colors = ['#2ca02c', '#ff7f0e', '#1f77b4']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    bars1 = ax1.bar(labels, wait_times, color=colors, edgecolor='black', alpha=0.8)
    ax1.set_title('Порівняння середнього часу очікування', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Час очікування 1 авто (с)', fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval} с', ha='center', va='bottom', fontweight='bold')

    bars2 = ax2.bar(labels, co2_emissions, color=colors, edgecolor='black', alpha=0.8)
    ax2.set_title('Порівняння загальних викидів CO2', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Викиди CO2 (кг)', fontsize=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 10, f'{yval} кг', ha='center', va='bottom', fontweight='bold')

    plt.suptitle('Ефективність методів керування трафіком', fontsize=16, y=1.05)
    plt.tight_layout()
    save_path = Path(__file__).parent / "stats" / "final_comparison_bars.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Графік порівняння збережено у {save_path}")

    plt.show()

if __name__ == "__main__":
    main()