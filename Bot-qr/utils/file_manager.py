import csv
import os
from datetime import datetime


def save_user(chat_id, username):
    """Сохраняет нового пользователя в CSV, если его ещё нет"""
    os.makedirs("data", exist_ok=True)
    file_path = "data/users.csv"

    # Проверяем, существует ли уже пользователь
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == str(chat_id):
                    return  # уже есть

    # Добавляем нового
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if os.path.getsize(file_path) == 0:
            writer.writerow(["chat_id", "username", "joined_at"])
        writer.writerow([chat_id, username, datetime.now().isoformat()])


def log_message(chat_id, text, is_bot=False):
    """
    Логирует сообщение в отдельный файл для каждого пользователя.
    Требование ТЗ: история сообщений в .txt файле.
    """
    os.makedirs("data/history", exist_ok=True)
    log_path = f"data/history/user_{chat_id}.log"
    role = "BOT" if is_bot else "USER"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {text}\n")


def generate_report():
    """Генерирует отчёт о работе бота за день (требование ТЗ)"""
    os.makedirs("data", exist_ok=True)
    report_path = f"data/report_{datetime.now().strftime('%Y%m%d')}.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Отчёт за {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("=" * 40 + "\n\n")

        if os.path.exists("data/users.csv"):
            with open("data/users.csv", "r", encoding="utf-8") as uf:
                f.write("Пользователи:\n")
                f.write(uf.read())
        else:
            f.write("Нет пользователей\n")

    return report_path