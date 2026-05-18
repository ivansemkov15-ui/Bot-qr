import os
import json
import time
import requests
from dotenv import load_dotenv

from utils.file_manager import generate_report
from utils.schedule_tasks import ScheduleWrapper  # планировщик
from handlers import process_message, send_message

from keyboards import main_keyboard

# Загружаем переменные из .env файла
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", 0))

# Загружаем конфиги
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open("tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

with open("greeting.txt", "r", encoding="utf-8") as f:
    GREETING_TEXT = f.read()

# Базовый URL для запросов к Telegram API
URL = f"https://api.telegram.org/bot{TOKEN}"

# last_update_id нужен, чтобы не обрабатывать одни и те же сообщения дважды
last_update_id = 0

def get_updates(offset=None):
    """Получает новые сообщения от Telegram. offset пропускает уже обработанные."""
    params = {"timeout": 30, "offset": offset}
    try:
        resp = requests.get(f"{URL}/getUpdates", params=params, timeout=30)
        return resp.json().get("result", [])
    except:
        return []

def morning_greeting():
    """Отправляет утреннее приветствие админу (вызывается планировщиком в 8:00)"""
    send_message(ADMIN_ID, f"🌅 {GREETING_TEXT}", URL)

def evening_report():
    """Генерирует и отправляет отчёт админу (вызывается планировщиком в 23:55)"""
    report_path = generate_report()
    with open(report_path, "rb") as f:
        requests.post(f"{URL}/sendDocument", data={"chat_id": ADMIN_ID}, files={"document": f}, timeout=30)

def main():
    global last_update_id
    print("QR-бот запущен")

    # Настройка планировщика задач
    schedule = ScheduleWrapper()
    schedule.add_task(tasks["greeting_time"], morning_greeting)
    schedule.add_task(tasks["report_time"], evening_report)
    schedule.start()  # запускаем в отдельном потоке

    # Основной цикл опроса (polling)
    while True:
        # Получаем новые сообщения, начиная с last_update_id + 1
        updates = get_updates(offset=last_update_id + 1)

        for update in updates:
            last_update_id = update["update_id"]  # обновляем ID последнего обработанного сообщения
            msg = update.get("message")
            if msg:
                process_message(msg, URL)  # вся логика обработки в handlers.py

        #getUpdates выполняется не чаще раза в секунду
        time.sleep(config["polling_interval"])

if __name__ == "__main__":
    main()