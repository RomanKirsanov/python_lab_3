import sqlite3
import datetime
from typing import List
from core.models import Habit, HabitStatus

class Database:
    def __init__(self, db_path: str = "habits.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    target_days INTEGER DEFAULT 7,
                    creation_date TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS completions (
                    habit_id INTEGER,
                    date TEXT,
                    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                    UNIQUE(habit_id, date)
                )
            """)
    
    def save_habit(self, habit: Habit) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if habit.id is None:
                cursor.execute("""
                    INSERT INTO habits (name, description, target_days, creation_date, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (habit.name, habit.description, habit.target_days,
                      habit.creation_date.isoformat(), habit.status.value))
                habit.id = cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE habits 
                    SET name=?, description=?, target_days=?, status=?
                    WHERE id=?
                """, (habit.name, habit.description, habit.target_days,
                      habit.status.value, habit.id))
            
            cursor.execute("DELETE FROM completions WHERE habit_id=?", (habit.id,))
            for date in habit.completions:
                cursor.execute(
                    "INSERT OR IGNORE INTO completions (habit_id, date) VALUES (?, ?)",
                    (habit.id, date.isoformat())
                )
            
            conn.commit()
            return habit.id
    
    def load_habits(self) -> List[Habit]:
        habits = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM habits ORDER BY id")
            for row in cursor.fetchall():
                cursor.execute(
                    "SELECT date FROM completions WHERE habit_id=? ORDER BY date",
                    (row['id'],)
                )
                completions = [
                    datetime.date.fromisoformat(date_row[0]) 
                    for date_row in cursor.fetchall()
                ]
                
                habit = Habit(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or "",
                    target_days=row['target_days'],
                    creation_date=datetime.date.fromisoformat(row['creation_date']),
                    status=HabitStatus(row['status']),
                    completions=completions
                )
                habits.append(habit)
        
        return habits
    
    def delete_habit(self, habit_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    
    def get_habit_stats(self, habit_id: int) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM habits WHERE id=?", (habit_id,))
            habit_row = cursor.fetchone()
            
            if not habit_row:
                return {}
            
            cursor.execute(
                "SELECT COUNT(*) FROM completions WHERE habit_id=?",
                (habit_id,)
            )
            completions_count = cursor.fetchone()[0]
            
            return {
                "id": habit_id,
                "completions_count": completions_count,
                "target_days": habit_row[3],
                "completion_rate": completions_count / habit_row[3] if habit_row[3] > 0 else 0
            }