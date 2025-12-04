import pytest
import datetime
import tempfile
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.models import Habit, HabitStatus
from core.database import Database

class TestHabitModel:
    def test_habit_creation(self):
        habit = Habit(name="Тест", description="Описание", target_days=30)
        assert habit.name == "Тест"
        assert habit.description == "Описание"
        assert habit.target_days == 30
        assert habit.status == HabitStatus.ACTIVE
    
    def test_mark_completed(self):
        habit = Habit(name="Тест")
        today = datetime.date.today()
        assert habit.mark_completed(today) == True
        assert today in habit.completions
        assert habit.mark_completed(today) == False  # Повторно не добавляется
    
    def test_completion_rate(self):
        habit = Habit(name="Тест", target_days=7)
        assert habit.get_completion_rate() == 0.0
        
        habit.mark_completed()
        assert habit.get_completion_rate() == 1/7
    
    def test_get_streak(self):
        habit = Habit(name="Тест")
        today = datetime.date.today()
        habit.mark_completed(today)
        habit.mark_completed(today - datetime.timedelta(days=1))
        assert habit.get_streak() == 2

class TestDatabase:
    @pytest.fixture
    def temp_db(self):
        """Фикстура для временной БД"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = Database(db_path)
        yield db
        
        # Удаляем временную БД
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_save_and_load_habit(self, temp_db):
        habit = Habit(name="БД тест", target_days=14)
        habit.mark_completed()
        
        habit_id = temp_db.save_habit(habit)
        assert habit_id is not None
        
        habits = temp_db.load_habits()
        assert len(habits) == 1
        assert habits[0].name == "БД тест"
        assert len(habits[0].completions) == 1
    
    def test_delete_habit(self, temp_db):
        habit = Habit(name="Для удаления")
        habit_id = temp_db.save_habit(habit)
        
        assert len(temp_db.load_habits()) == 1
        
        temp_db.delete_habit(habit_id)
        assert len(temp_db.load_habits()) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])