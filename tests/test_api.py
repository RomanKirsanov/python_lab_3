import pytest
import tempfile
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.main import app
from core.database import Database

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    """Фикстура для тестовой БД"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Монкируем БД в приложении
    original_db = app.state.db
    test_db = Database(db_path)
    app.state.db = test_db
    
    yield test_db
    
    # Восстанавливаем оригинальную БД
    app.state.db = original_db
    
    # Удаляем тестовую БД
    if os.path.exists(db_path):
        os.unlink(db_path)

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_habits_empty(client, test_db):
    response = client.get("/api/habits")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_get_habit(client, test_db):
    # Создаем привычку
    create_response = client.post("/api/habits", json={
        "name": "Тестовая привычка",
        "description": "Описание теста",
        "target_days": 30
    })
    assert create_response.status_code == 200
    
    data = create_response.json()
    assert data["name"] == "Тестовая привычка"
    assert "id" in data
    
    # Получаем все привычки
    get_response = client.get("/api/habits")
    assert get_response.status_code == 200
    habits = get_response.json()
    assert len(habits) == 1
    assert habits[0]["name"] == "Тестовая привычка"

def test_mark_completion(client, test_db):
    # Сначала создаем привычку
    create_response = client.post("/api/habits", json={
        "name": "Для выполнения",
        "target_days": 7
    })
    habit_id = create_response.json()["id"]
    
    # Отмечаем выполнение
    response = client.post(f"/api/habits/{habit_id}/complete")
    assert response.status_code == 200
    assert "message" in response.json()

def test_web_interface(client, test_db):
    response = client.get("/web")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])