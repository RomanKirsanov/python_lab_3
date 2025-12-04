from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from core.database import Database
from core.models import Habit
from web.main import get_db

router = APIRouter(prefix="/api/v2/habits", tags=["habits v2"])

# Дополнительные модели для v2 API
class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_days: Optional[int] = None

@router.get("/", response_model=List[dict])
async def get_all_habits(db: Database = Depends(get_db)):
    """Получить все привычки (v2)"""
    habits = db.load_habits()
    return [habit.to_dict() for habit in habits]

@router.get("/active", response_model=List[dict])
async def get_active_habits(db: Database = Depends(get_db)):
    """Получить только активные привычки"""
    habits = db.load_habits()
    active_habits = [h for h in habits if h.status.value == "active"]
    return [habit.to_dict() for habit in active_habits]

@router.get("/{habit_id}/stats")
async def get_habit_statistics(habit_id: int, db: Database = Depends(get_db)):
    """Получить детальную статистику привычки"""
    stats = db.get_habit_stats(habit_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Привычка не найдена")
    return stats

@router.put("/{habit_id}")
async def update_habit(
    habit_id: int, 
    habit_data: HabitUpdate,
    db: Database = Depends(get_db)
):
    """Обновить информацию о привычке"""
    habits = db.load_habits()
    for habit in habits:
        if habit.id == habit_id:
            # Обновляем поля, если они предоставлены
            if habit_data.name is not None:
                habit.name = habit_data.name
            if habit_data.description is not None:
                habit.description = habit_data.description
            if habit_data.target_days is not None:
                habit.target_days = habit_data.target_days
            
            db.save_habit(habit)
            return {"message": "Привычка обновлена", "habit": habit.to_dict()}
    
    raise HTTPException(status_code=404, detail="Привычка не найдена")