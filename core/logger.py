import logging
import sys
from datetime import datetime

def setup_logger(name="HabitTracker", log_file="habits.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый обработчик
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Глобальный логгер
logger = setup_logger()

def log_habit_created(habit_name: str):
    logger.info(f"Привычка создана: {habit_name}")

def log_habit_completed(habit_name: str, date: datetime = None):
    date_str = date.strftime("%Y-%m-%d") if date else datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Привычка выполнена: {habit_name} ({date_str})")

def log_habit_deleted(habit_name: str):
    logger.info(f"Привычка удалена: {habit_name}")

def log_error(error_msg: str, exc_info=None):
    logger.error(error_msg, exc_info=exc_info)