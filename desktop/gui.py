import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel,
    QMenuBar, QMenu, QMessageBox, QHBoxLayout, QTextEdit,
    QDialog, QDialogButtonBox, QDateEdit, QSpinBox, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction
import datetime
from core.database import Database
from core.models import Habit, HabitStatus
from core.logger import logger, log_habit_created, log_habit_completed, log_habit_deleted
from core.plotter import HabitPlotter

class AddHabitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить привычку")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Поля ввода
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название привычки")
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание (необязательно)")
        
        self.target_input = QSpinBox()
        self.target_input.setRange(1, 365)
        self.target_input.setValue(7)
        self.target_input.setPrefix("Цель: ")
        self.target_input.setSuffix(" дней")
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(QLabel("Цель:"))
        layout.addWidget(self.target_input)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_habit_data(self):
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "target_days": self.target_input.value()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.plotter = HabitPlotter(self.db)
        self.init_ui()
        self.load_habits()
    
    def init_ui(self):
        self.setWindowTitle("Трекер привычек")
        self.setGeometry(100, 100, 1000, 700)
        
        # Меню
        self.create_menu()
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Таблица привычек
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Описание", "Цель", "Выполнено", "Прогресс", "Серия"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Добавить привычку")
        self.add_btn.clicked.connect(self.show_add_dialog)
        
        self.complete_btn = QPushButton("✅ Отметить выполнение")
        self.complete_btn.clicked.connect(self.mark_completion)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_habit)
        
        self.plot_btn = QPushButton("📊 Графики")
        self.plot_btn.clicked.connect(self.show_plots)
        
        control_layout.addWidget(self.add_btn)
        control_layout.addWidget(self.complete_btn)
        control_layout.addWidget(self.delete_btn)
        control_layout.addWidget(self.plot_btn)
        
        main_layout.addLayout(control_layout)
        
        # Лог
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(QLabel("Лог активности:"))
        main_layout.addWidget(self.log_text)
        
        central_widget.setLayout(main_layout)
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        export_action = QAction("Экспорт данных", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Вид
        view_menu = menubar.addMenu("Вид")
        
        refresh_action = QAction("Обновить", self)
        refresh_action.triggered.connect(self.load_habits)
        view_menu.addAction(refresh_action)
        
        # Меню Помощь
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_habits(self):
        habits = self.db.load_habits()
        self.table.setRowCount(len(habits))
        
        for i, habit in enumerate(habits):
            self.table.setItem(i, 0, QTableWidgetItem(str(habit.id or "")))
            self.table.setItem(i, 1, QTableWidgetItem(habit.name))
            self.table.setItem(i, 2, QTableWidgetItem(habit.description))
            self.table.setItem(i, 3, QTableWidgetItem(str(habit.target_days)))
            self.table.setItem(i, 4, QTableWidgetItem(str(len(habit.completions))))
            
            # Прогресс
            progress = habit.get_completion_rate()
            progress_item = QTableWidgetItem(f"{progress:.1%}")
            if progress >= 1.0:
                progress_item.setBackground(Qt.green)
            elif progress >= 0.7:
                progress_item.setBackground(Qt.yellow)
            self.table.setItem(i, 5, progress_item)
            
            # Серия
            streak_item = QTableWidgetItem(str(habit.get_streak()))
            if habit.get_streak() > 0:
                streak_item.setBackground(Qt.green)
            self.table.setItem(i, 6, streak_item)
        
        self.table.resizeColumnsToContents()
    
    def show_add_dialog(self):
        dialog = AddHabitDialog(self)
        if dialog.exec():
            data = dialog.get_habit_data()
            if not data["name"]:
                QMessageBox.warning(self, "Ошибка", "Введите название привычки")
                return
            
            habit = Habit(
                name=data["name"],
                description=data["description"],
                target_days=data["target_days"]
            )
            
            try:
                self.db.save_habit(habit)
                log_habit_created(habit.name)
                self.log_text.append(f"[{datetime.datetime.now()}] Добавлена привычка: {habit.name}")
                self.load_habits()
            except Exception as e:
                logger.error(f"Ошибка при сохранении привычки: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить привычку: {str(e)}")
    
    def mark_completion(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите привычку в таблице")
            return
        
        habit_id = int(self.table.item(selected_row, 0).text())
        habits = self.db.load_habits()
        
        for habit in habits:
            if habit.id == habit_id:
                success = habit.mark_completed()
                if success:
                    self.db.save_habit(habit)
                    log_habit_completed(habit.name)
                    self.log_text.append(f"[{datetime.datetime.now()}] Привычка '{habit.name}' выполнена")
                    self.load_habits()
                    QMessageBox.information(self, "Успех", f"Привычка '{habit.name}' отмечена как выполненная")
                else:
                    QMessageBox.information(self, "Информация", "Эта привычка уже была отмечена сегодня")
                break
    
    def delete_habit(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите привычку в таблице")
            return
        
        habit_id = int(self.table.item(selected_row, 0).text())
        habit_name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            f"Удалить привычку '{habit_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_habit(habit_id)
                log_habit_deleted(habit_name)
                self.log_text.append(f"[{datetime.datetime.now()}] Удалена привычка: {habit_name}")
                self.load_habits()
            except Exception as e:
                logger.error(f"Ошибка при удалении привычки: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить привычку: {str(e)}")
    
    def show_plots(self):
        habits = self.db.load_habits()
        if not habits:
            QMessageBox.information(self, "Информация", "Нет привычек для отображения графиков")
            return
        
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            # График для выбранной привычки
            habit_id = int(self.table.item(selected_row, 0).text())
            for habit in habits:
                if habit.id == habit_id:
                    fig = self.plotter.plot_habit_progress(habit)
                    fig.show()
                    break
        else:
            # График для всех привычек
            fig = self.plotter.plot_all_habits(habits)
            fig.show()
    
    def export_data(self):
        habits = self.db.load_habits()
        if not habits:
            QMessageBox.information(self, "Информация", "Нет данных для экспорта")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт данных", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Название;Описание;Цель;Выполнено;Прогресс;Серия\n")
                    for habit in habits:
                        progress = habit.get_completion_rate()
                        f.write(f"{habit.name};{habit.description};{habit.target_days};"
                               f"{len(habit.completions)};{progress:.1%};{habit.get_streak()}\n")
                
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
            except Exception as e:
                logger.error(f"Ошибка при экспорте данных: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")
    
    def show_about(self):
        QMessageBox.about(self, "О программе",
            "Трекер привычек v1.0\n\n"
            "Приложение для отслеживания привычек\n"
            "Разработано для лабораторной работы №3\n\n"
            "Функции:\n"
            "- Добавление/удаление привычек\n"
            "- Отслеживание выполнения\n"
            "- Визуализация прогресса\n"
            "- Логирование активности"
        )