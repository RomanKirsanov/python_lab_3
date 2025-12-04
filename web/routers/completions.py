from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import datetime
from core.database import Database
from core.models import Habit
from web.main import get_db

router = APIRouter(prefix="/api/v2/completions", tags=["completions v2"])

class CompletionCreate(BaseModel):
    date: Optional[str] = None  # Дата в формате YYYY-MM-DD

@router.get("/habit/{habit_id}")
async def get_habit_completions(
    habit_id: int, 
    db: Database = Depends(get_db)
):
    """Получить все выполнения конкретной привычки"""
    habits = db.load_habits()
    for habit in habits:
        if habit.id == habit_id:
            return {
                "habit_id": habit_id,
                "habit_name": habit.name,
                "completions": [d.isoformat() for d in habit.completions],
                "total": len(habit.completions)
            }
    
    raise HTTPException(status_code=404, detail="Привычка не найдена")

@router.get("/date/{date}")
async def get_completions_by_date(
    date: str,
    db: Database = Depends(get_db)
):
    """Получить все выполнения за определенную дату"""
    try:
        target_date = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD")
    
    habits = db.load_habits()
    completions = []
    
    for habit in habits:
        if target_date in habit.completions:
            completions.append({
                "habit_id": habit.id,
                "habit_name": habit.name,
                "date": date
            })
    
    return {
        "date": date,
        "total_completions": len(completions),
        "completions": completions
    }

@router.post("/habit/{habit_id}")
async def create_completion(
    habit_id: int,
    completion_data: Optional[CompletionCreate] = None,
    db: Database = Depends(get_db)
):
    """Создать отметку о выполнении с возможностью указать дату"""
    habits = db.load_habits()
    
    for habit in habits:
        if habit.id == habit_id:
            date = None
            if completion_data and completion_data.date:
                try:
                    date = datetime.date.fromisoformat(completion_data.date)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Неверный формат даты")
            
            if habit.mark_completed(date):
                db.save_habit(habit)
                return {
                    "message": "Выполнение добавлено",
                    "habit_id": habit_id,
                    "habit_name": habit.name,
                    "date": date.isoformat() if date else datetime.date.today().isoformat()
                }
            else:
                return {
                    "message": "Привычка уже была выполнена в эту дату",
                    "habit_id": habit_id,
                    "date": date.isoformat() if date else datetime.date.today().isoformat()
                }
    
    raise HTTPException(status_code=404, detail="Привычка не найдена")

@router.delete("/habit/{habit_id}/date/{date}")
async def delete_completion(
    habit_id: int,
    date: str,
    db: Database = Depends(get_db)
):
    """Удалить отметку о выполнении за конкретную дату"""
    try:
        target_date = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")
    
    habits = db.load_habits()
    
    for habit in habits:
        if habit.id == habit_id:
            if target_date in habit.completions:
                habit.completions.remove(target_date)
                db.save_habit(habit)
                return {
                    "message": "Выполнение удалено",
                    "habit_id": habit_id,
                    "date": date
                }
            else:
                raise HTTPException(status_code=404, detail="Выполнение не найдено")
    
    raise HTTPException(status_code=404, detail="Привычка не найдена")