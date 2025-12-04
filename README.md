Трекер привычек

Трекер привычек с десктопным и веб-интерфейсом. 

### Десктопное приложение (PySide6)
- ✅ Добавление/удаление привычек
- ✅ Отслеживание выполнения
- ✅ Таблица с прогрессом
- ✅ Графики выполнения
- ✅ Логирование активности
- ✅ Экспорт данных

### Веб-приложение (FastAPI)
- ✅ REST API для управления привычками
- ✅ Веб-интерфейс с графиками
- ✅ Статистика выполнения
  

Запуск

### Способ 1: 

# Клонирование и установка
git clone <репозиторий>
cd python_lab_3

# Установка зависимостей
pip install -r requirements.txt

# Запуск веб-сервера
python run.py --mode web

# Или десктопного приложения
python run.py --mode desktop

# Или оба режима
python run.py --mode both

Способ 2: Через Docker

docker-compose up web

# Запуск тестов
docker-compose up test

Тестирование

# Все тесты
pytest tests/ -v

# С покрытием кода
pytest --cov=core --cov=web tests/

# Конкретный тестовый файл
pytest tests/test_core.py -v


Docker команды

# Сборка образа
docker build -t habit-tracker .

# Запуск контейнера
docker run -p 8000:8000 habit-tracker

# Просмотр логов
docker-compose logs -f web

# Остановка всех сервисов
docker-compose down

# Пересборка и запуск
docker-compose up --build
