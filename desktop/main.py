import sys
from PySide6.QtWidgets import QApplication
from desktop.gui import MainWindow
from core.logger import logger

def main():
    """Главная функция для запуска десктопного приложения"""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        logger.info("Десктопное приложение запущено")
        return app.exec()
    except Exception as e:
        logger.error(f"Ошибка при запуске десктопного приложения: {e}", exc_info=True)
        print(f"Ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())