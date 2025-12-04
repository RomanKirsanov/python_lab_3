import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class HabitStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class Habit:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    target_days: int = 7
    creation_date: datetime.date = field(default_factory=datetime.date.today)
    status: HabitStatus = HabitStatus.ACTIVE
    completions: List[datetime.date] = field(default_factory=list)
    
    def mark_completed(self, date: Optional[datetime.date] = None) -> bool:
        if date is None:
            date = datetime.date.today()
        if date not in self.completions:
            self.completions.append(date)
            return True
        return False
    
    def get_completion_rate(self) -> float:
        if self.target_days == 0:
            return 0.0
        return min(len(self.completions) / self.target_days, 1.0)
    
    def get_streak(self) -> int:
        if not self.completions:
            return 0
        
        dates = sorted(self.completions, reverse=True)
        streak = 0
        current_date = datetime.date.today()
        
        for i in range(len(dates)):
            if dates[i] == current_date - datetime.timedelta(days=i):
                streak += 1
            else:
                break
        return streak
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_days": self.target_days,
            "creation_date": self.creation_date.isoformat(),
            "status": self.status.value,
            "completions": [d.isoformat() for d in self.completions],
            "completion_rate": self.get_completion_rate(),
            "streak": self.get_streak()
        }

class HabitManager:
    def __init__(self):
        self.habits: List[Habit] = []
    
    def add_habit(self, habit: Habit):
        self.habits.append(habit)
    
    def remove_habit(self, habit_name: str):
        self.habits = [h for h in self.habits if h.name != habit_name]
    
    def get_habit(self, name: str) -> Optional[Habit]:
        for habit in self.habits:
            if habit.name == name:
                return habit
        return None