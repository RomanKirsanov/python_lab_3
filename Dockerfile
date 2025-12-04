FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/data /app/logs

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 habituser && chown -R habituser:habituser /app
USER habituser

# Порт для веб-сервера
EXPOSE 8000

# Команда по умолчанию
CMD ["python", "run.py", "--mode", "web"]