"""
Альтернативный API файл (можно использовать вместо web/main.py)
"""
from fastapi import FastAPI
from web.main import (
    get_habits, create_habit, get_habit, 
    delete_habit, complete_habit, get_stats
)

# Создаем отдельное FastAPI приложение для API
api_app = FastAPI(
    title="Habit Tracker API Only",
    description="Только API без веб-интерфейса",
    version="1.0.0"
)

# Подключаем те же эндпоинты
api_app.get("/api/habits")(get_habits)
api_app.post("/api/habits")(create_habit)
api_app.get("/api/habits/{habit_id}")(get_habit)
api_app.delete("/api/habits/{habit_id}")(delete_habit)
api_app.post("/api/habits/{habit_id}/complete")(complete_habit)
api_app.get("/api/stats")(get_stats)

@api_app.get("/")
async def api_root():
    return {
        "message": "Habit Tracker API (только API)",
        "endpoints": [
            "GET /api/habits",
            "POST /api/habits",
            "GET /api/habits/{id}",
            "DELETE /api/habits/{id}",
            "POST /api/habits/{id}/complete",
            "GET /api/stats"
        ]
    }