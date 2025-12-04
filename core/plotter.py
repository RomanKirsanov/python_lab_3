import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from typing import Optional
from core.models import Habit
from core.database import Database

class HabitPlotter:
    def __init__(self, db: Optional[Database] = None):
        self.db = db
    
    def plot_habit_progress(self, habit: Habit) -> Figure:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # График выполнения по дням
        if habit.completions:
            dates = sorted(habit.completions)
            date_strings = [d.strftime("%Y-%m-%d") for d in dates]
            
            ax1.plot(range(len(dates)), range(1, len(dates) + 1), 'o-', linewidth=2)
            ax1.set_xlabel('Дни')
            ax1.set_ylabel('Выполнено раз')
            ax1.set_title(f'Прогресс: {habit.name}')
            ax1.grid(True, alpha=0.3)
            ax1.set_xticks(range(len(dates)))
            ax1.set_xticklabels(date_strings, rotation=45)
        
        # Круговая диаграмма прогресса
        completed = len(habit.completions)
        remaining = max(0, habit.target_days - completed)
        
        if habit.target_days > 0:
            labels = ['Выполнено', 'Осталось']
            sizes = [completed, remaining]
            colors = ['#4CAF50', '#FF6B6B']
            
            ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            ax2.set_title(f'Прогресс: {completed}/{habit.target_days}')
        
        plt.tight_layout()
        return fig
    
    def plot_all_habits(self, habits: list) -> Figure:
        if not habits:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   ha='center', va='center', fontsize=12)
            return fig
        
        names = [h.name for h in habits]
        completed = [len(h.completions) for h in habits]
        targets = [h.target_days for h in habits]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(names))
        bar_width = 0.35
        
        bars1 = ax.bar([i - bar_width/2 for i in x], completed, bar_width, 
                      label='Выполнено', color='lightblue')
        bars2 = ax.bar([i + bar_width/2 for i in x], targets, bar_width, 
                      label='Цель', color='lightgreen', alpha=0.7)
        
        ax.set_xlabel('Привычки')
        ax.set_ylabel('Дни')
        ax.set_title('Сравнение выполнения привычек')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        
        # Добавляем значения на столбцы
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def save_plot(self, fig: Figure, filename: str = "plot.png"):
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)