import schedule
import threading
import time


class ScheduleWrapper:
    """
    Обёртка над библиотекой schedule.
    Запускает задачи в отдельном потоке, чтобы не блокировать основной цикл.
    """

    def __init__(self):
        self.tasks = []

    def add_task(self, time_str, func):
        """Добавляет задачу на определённое время (например, '08:00')"""
        schedule.every().day.at(time_str).do(func)
        self.tasks.append((time_str, func))

    def start(self):
        """Запускает планировщик в фоновом потоке"""

        def run():
            while True:
                schedule.run_pending()  # проверяет, не пора ли выполнить задачи
                time.sleep(1)

        # daemon=True — поток завершится при закрытии main
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        print("Планировщик запущен")