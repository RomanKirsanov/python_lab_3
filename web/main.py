from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import datetime
from core.database import Database
from core.models import Habit
from core.logger import logger

app = FastAPI(
    title="Habit Tracker API",
    description="Веб-версия трекера привычек",
    version="1.0.0"
)

# Инициализация БД
db = Database()
app.state.db = db

# Pydantic модели
class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    target_days: int = 7

class HabitResponse(BaseModel):
    id: int
    name: str
    description: str
    target_days: int
    creation_date: str
    status: str
    completions: List[str]
    completion_rate: float
    streak: int

# Зависимость для получения БД
def get_db():
    return app.state.db

# Основные endpoints
@app.get("/")
async def root():
    return {
        "message": "Habit Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "web_interface": "/web"
    }

@app.get("/api/habits", response_model=List[HabitResponse])
async def get_habits(db: Database = Depends(get_db)):
    """Получить все привычки"""
    habits = db.load_habits()
    return [habit.to_dict() for habit in habits]

@app.post("/api/habits", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate, 
    db: Database = Depends(get_db)
):
    """Создать новую привычку"""
    habit = Habit(
        name=habit_data.name,
        description=habit_data.description,
        target_days=habit_data.target_days
    )
    
    try:
        habit_id = db.save_habit(habit)
        habit.id = habit_id
        logger.info(f"Создана привычка через API: {habit.name}")
        return habit.to_dict()
    except Exception as e:
        logger.error(f"Ошибка при создании привычки: {e}")
        raise HTTPException(status_code=500, detail="Не удалось создать привычку")

@app.get("/api/habits/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: int, 
    db: Database = Depends(get_db)
):
    """Получить конкретную привычку"""
    habits = db.load_habits()
    for habit in habits:
        if habit.id == habit_id:
            return habit.to_dict()
    
    raise HTTPException(status_code=404, detail="Привычка не найдена")

@app.delete("/api/habits/{habit_id}")
async def delete_habit(
    habit_id: int, 
    db: Database = Depends(get_db)
):
    """Удалить привычку"""
    try:
        db.delete_habit(habit_id)
        logger.info(f"Удалена привычка через API: ID {habit_id}")
        return {"message": "Привычка удалена"}
    except Exception as e:
        logger.error(f"Ошибка при удалении привычки: {e}")
        raise HTTPException(status_code=500, detail="Не удалось удалить привычку")

@app.post("/api/habits/{habit_id}/complete")
async def complete_habit(
    habit_id: int, 
    db: Database = Depends(get_db)
):
    """Отметить выполнение привычки"""
    habits = db.load_habits()
    for habit in habits:
        if habit.id == habit_id:
            if habit.mark_completed():
                db.save_habit(habit)
                logger.info(f"Привычка выполнена через API: {habit.name}")
                return {
                    "message": "Привычка отмечена как выполненная",
                    "date": datetime.date.today().isoformat()
                }
            else:
                return {
                    "message": "Привычка уже была выполнена сегодня",
                    "date": datetime.date.today().isoformat()
                }
    
    raise HTTPException(status_code=404, detail="Привычка не найдена")

@app.get("/api/stats")
async def get_stats(db: Database = Depends(get_db)):
    """Получить общую статистику"""
    habits = db.load_habits()
    
    total_habits = len(habits)
    active_habits = len([h for h in habits if h.status.value == "active"])
    total_completions = sum(len(h.completions) for h in habits)
    
    avg_completion_rate = 0
    if habits:
        avg_completion_rate = sum(h.get_completion_rate() for h in habits) / len(habits)
    
    return {
        "total_habits": total_habits,
        "active_habits": active_habits,
        "total_completions": total_completions,
        "average_completion_rate": round(avg_completion_rate, 2),
        "most_completed_habit": max(habits, key=lambda h: len(h.completions)).name if habits else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Веб-интерфейс"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Habit Tracker Web</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .add-form {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background: #2980b9;
            }
            .habit-item {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
                padding: 15px;
                background: #ecf0f1;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Habit Tracker</h1>
            
            <div class="stats" id="stats">
                <div>Всего привычек: <span id="total-habits">0</span></div>
                <div>Всего выполнений: <span id="total-completions">0</span></div>
            </div>
            
            <div class="add-form">
                <input type="text" id="habit-name" placeholder="Название привычки" required>
                <input type="number" id="habit-target" placeholder="Цель (дней)" value="7">
                <button onclick="addHabit()">Добавить</button>
            </div>
            
            <div id="habits-list">
                <!-- Список привычек будет здесь -->
            </div>
        </div>
        
        <script>
            async function loadHabits() {
                const response = await fetch('/api/habits');
                const habits = await response.json();
                
                // Обновляем статистику
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                document.getElementById('total-habits').textContent = stats.total_habits;
                document.getElementById('total-completions').textContent = stats.total_completions;
                
                // Отображаем привычки
                const habitsList = document.getElementById('habits-list');
                habitsList.innerHTML = '';
                
                habits.forEach(habit => {
                    const habitElement = document.createElement('div');
                    habitElement.className = 'habit-item';
                    
                    const progress = Math.min(habit.completion_rate * 100, 100);
                    const progressBar = `
                        <div style="width: 100%; background: #ddd; border-radius: 3px; margin: 5px 0;">
                            <div style="width: ${progress}%; background: #2ecc71; height: 20px; border-radius: 3px;"></div>
                        </div>
                    `;
                    
                    habitElement.innerHTML = `
                        <div>
                            <strong>${habit.name}</strong><br>
                            <small>${habit.description || 'Нет описания'}</small><br>
                            ${progressBar}
                            <small>${habit.completions.length}/${habit.target_days} дней (${progress.toFixed(1)}%) | Серия: ${habit.streak}</small>
                        </div>
                        <div>
                            <button onclick="completeHabit(${habit.id})">✅ Выполнено</button>
                            <button onclick="deleteHabit(${habit.id})" style="background: #e74c3c">🗑️ Удалить</button>
                        </div>
                    `;
                    
                    habitsList.appendChild(habitElement);
                });
            }
            
            async function addHabit() {
                const name = document.getElementById('habit-name').value;
                const target = document.getElementById('habit-target').value;
                
                if (!name) {
                    alert('Введите название привычки');
                    return;
                }
                
                await fetch('/api/habits', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        target_days: parseInt(target) || 7
                    })
                });
                
                document.getElementById('habit-name').value = '';
                loadHabits();
            }
            
            async function completeHabit(habitId) {
                await fetch(`/api/habits/${habitId}/complete`, {
                    method: 'POST'
                });
                loadHabits();
            }
            
            async function deleteHabit(habitId) {
                if (confirm('Удалить эту привычку?')) {
                    await fetch(`/api/habits/${habitId}`, {
                        method: 'DELETE'
                    });
                    loadHabits();
                }
            }
            
            // Загружаем привычки при загрузке страницы
            loadHabits();
        </script>
    </body>
    </html>
    """