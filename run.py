#!/usr/bin/env python3
"""
Главный файл запуска Habit Tracker.
Запускает десктопное приложение и/или веб-сервер.
"""

import sys
import argparse
import threading
import webbrowser
from core.logger import logger, setup_logger
import os

def run_desktop():
    """Запуск десктопного приложения"""
    try:
        from desktop.main import main as desktop_main
        logger.info("Запуск десктопного приложения...")
        return desktop_main()
    except ImportError as e:
        logger.error(f"Ошибка импорта десктопного модуля: {e}")
        print("Десктопное приложение недоступно.")
        print("Установите PySide6: pip install PySide6")
        return 1
    except Exception as e:
        logger.error(f"Ошибка при запуске десктопного приложения: {e}", exc_info=True)
        return 1

def run_web():
    """Запуск веб-сервера"""
    try:
        import uvicorn
        from web.main import app
        
        logger.info("Запуск веб-сервера на http://localhost:8000")
        print("=" * 50)
        print("🚀 Habit Tracker Web Server запущен!")
        print("📊 Веб-интерфейс: http://localhost:8000/web")
        print("📚 API документация: http://localhost:8000/docs")
        print("❤️  Health check: http://localhost:8000/health")
        print("=" * 50)
        
        # Автоматически открываем браузер
        try:
            webbrowser.open("http://localhost:8000/web")
        except:
            pass  # Игнорируем ошибки открытия браузера
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False  # Для production установите False
        )
    except ImportError as e:
        logger.error(f"Ошибка импорта веб-модуля: {e}")
        print("Веб-сервер недоступен.")
        print("Установите зависимости: pip install fastapi uvicorn")
        return 1
    except Exception as e:
        logger.error(f"Ошибка при запуске веб-сервера: {e}", exc_info=True)
        return 1

def run_both():
    """Запуск десктопного приложения и веб-сервера одновременно"""
    logger.info("Запуск комбинированного режима...")
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Даем время серверу запуститься
    import time
    time.sleep(2)
    
    # Запускаем десктопное приложение
    return run_desktop()

def run_tests():
    """Запуск тестов"""
    try:
        import pytest
        logger.info("Запуск тестов...")
        return pytest.main(["tests/", "-v", "--tb=short"])
    except ImportError:
        print("pytest не установлен. Установите: pip install pytest")
        return 1

def check_requirements():
    """Проверка установленных зависимостей"""
    required = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn[standard]"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic")
    ]
    
    missing = []
    for package, install_name in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(install_name)
    
    if missing:
        print("❌ Отсутствуют зависимости:")
        for dep in missing:
            print(f"   - {dep}")
        print(f"\nУстановите: pip install {' '.join(missing)}")
        return False
    return True

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Habit Tracker - трекер привычек",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run.py                    # Запуск веб-сервера (по умолчанию)
  python run.py --mode desktop     # Запуск десктопного приложения
  python run.py --mode both        # Запуск обоих режимов
  python run.py --mode test        # Запуск тестов
  python run.py --help            # Показать эту справку
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['desktop', 'web', 'both', 'test'], 
        default='web',
        help='Режим запуска (по умолчанию: web)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Уровень логирования'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Не открывать браузер автоматически'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Порт для веб-сервера (по умолчанию: 8000)'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Проверить зависимости и выйти'
    )
    
    args = parser.parse_args()
    
   
    setup_logger()  


    import logging
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger("HabitTracker").setLevel(log_level)
    logger.info(f"Запуск Habit Tracker в режиме: {args.mode}")
    
    # Проверка зависимостей
    if args.check_deps:
        if check_requirements():
            print("✅ Все зависимости установлены")
            return 0
        else:
            return 1
    
    # Запуск в выбранном режиме
    if args.mode == 'desktop':
        return run_desktop()
    elif args.mode == 'web':
        if args.no_browser:
            os.environ['NO_BROWSER'] = '1'
        if args.port != 8000:
            os.environ['PORT'] = str(args.port)
        return run_web()
    elif args.mode == 'both':
        return run_both()
    elif args.mode == 'test':
        return run_tests()

if __name__ == "__main__":
    sys.exit(main())