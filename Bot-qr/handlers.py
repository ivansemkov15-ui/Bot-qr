import json
import requests
from utils.file_manager import save_user, log_message
from utils.qr_generator import generate_qr, generate_colored_qr
from states import *
from keyboards import *


def send_message(chat_id, text, url, keyboard=None):
    """Отправка текстового сообщения. Если передан keyboard, добавляет Reply-клавиатуру."""
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = json.dumps(keyboard)  # сериализуем клавиатуру в JSON
    try:
        requests.post(f"{url}/sendMessage", json=payload, timeout=30)
    except Exception as e:
        print(f"Ошибка отправки: {e}")


def send_photo(chat_id, photo_path, url):
    """Отправка PNG"""
    with open(photo_path, "rb") as f:
        requests.post(f"{url}/sendPhoto", data={"chat_id": chat_id}, files={"photo": f}, timeout=30)


def send_document(chat_id, file_path, url):
    """Отправка SVG"""
    with open(file_path, "rb") as f:
        requests.post(f"{url}/sendDocument", data={"chat_id": chat_id}, files={"document": f}, timeout=30)


def process_message(msg, url):
    """Главный обработчик. Определяет тип сообщения и вызывает нужную логику."""
    chat_id = msg["chat"]["id"]
    username = msg["from"].get("username", "unknown")
    text = msg.get("text", "")
    location = msg.get("location")

    # Логируем и сохраняем пользователя
    log_message(chat_id, text)
    save_user(chat_id, username)

    state = get_state(chat_id)  # текущее состояние FSM

    # Геолокация
    if location:
        handle_location(chat_id, location["latitude"], location["longitude"], url)
        return

    # Системные кнопки отмены и назад
    if text == "❌ Отмена":
        clear_state(chat_id)
        send_message(chat_id, "Создание отменено", url, main_keyboard())
        return

    if text == "◀️ Назад":
        if state == STATE_WAITING_QR_COLOR:
            clear_state(chat_id)
            send_message(chat_id, "Создание отменено", url, main_keyboard())
        elif state == STATE_WAITING_QR_FORMAT:
            set_state(chat_id, STATE_WAITING_QR_COLOR)
            send_message(chat_id, "Выберите цвет", url, color_keyboard())
        else:
            clear_state(chat_id)
            send_message(chat_id, "Главное меню", url, main_keyboard())
        return

    # Обработка по состояниям FSM (пошаговый диалог)
    if state == STATE_WAITING_QR_TEXT:
        # Шаг 1: пользователь ввёл текст
        set_temp(chat_id, "text", text)
        set_state(chat_id, STATE_WAITING_QR_COLOR)
        send_message(chat_id, f"Текст: {text}\n\nВыберите цвет", url, color_keyboard())

    elif state == STATE_WAITING_QR_COLOR:
        # Шаг 2: пользователь выбирает цвет
        if text in ["⚫ Черный", "🔴 Красный", "🔵 Синий", "🟢 Зеленый", "🟡 Желтый", "🟣 Фиолетовый"]:
            color_hex = get_color_code(text)
            set_temp(chat_id, "color", color_hex)
            set_state(chat_id, STATE_WAITING_QR_FORMAT)
            send_message(chat_id, f"Цвет: {text}\n\nВыберите формат", url, format_keyboard())
        elif text == "🎨 Свой цвет (HEX)":
            send_message(chat_id, "Введите цвет в формате HEX (#RRGGBB)", url, back_keyboard())
        elif text.startswith("#") and len(text) == 7:
            set_temp(chat_id, "color", text)
            set_state(chat_id, STATE_WAITING_QR_FORMAT)
            send_message(chat_id, f"Цвет: {text}\n\nВыберите формат", url, format_keyboard())
        else:
            send_message(chat_id, "Выберите цвет из клавиатуры", url, color_keyboard())

    elif state == STATE_WAITING_QR_FORMAT:
        # Шаг 3: пользователь выбирает формат - генерируем QR
        if text in ["📱 PNG", "📄 SVG"]:
            txt = get_temp(chat_id, "text")
            color = get_temp(chat_id, "color")
            fmt = "png" if "PNG" in text else "svg"

            send_message(chat_id, "Генерация QR-кода...", url)

            # Если выбран цветной QR и формат PNG - используем цветной API
            if color and color != "#000000" and fmt == "png":
                path = generate_colored_qr(txt, color)
            else:
                path = generate_qr(txt, fmt)

            if path:
                if fmt == "png":
                    send_photo(chat_id, path, url)
                else:
                    send_document(chat_id, path, url)
                log_message(chat_id, f"QR ({fmt}) для: {txt}", is_bot=True)
                send_message(chat_id, "QR-код готов!", url, main_keyboard())
            else:
                send_message(chat_id, "Ошибка генерации", url, main_keyboard())
            clear_state(chat_id)
        else:
            send_message(chat_id, "Выберите формат PNG или SVG", url, format_keyboard())

    else:
        # Обычные команды (пользователь не в диалоге)
        if text == "/start":
            save_user(chat_id, username)
            clear_state(chat_id)
            send_message(chat_id, "QR-бот\n\nНажми «Создать QR-код»", url, main_keyboard())
        elif text == "/help":
            send_message(chat_id, "/start - меню\n/me - мой ID\n/help - помощь", url, main_keyboard())
        elif text == "/me":
            send_message(chat_id, f"ID: <code>{chat_id}</code>", url)
        elif text == "🔲 Создать QR-код":
            set_state(chat_id, STATE_WAITING_QR_TEXT)
            send_message(chat_id, "Введите текст или ссылку", url, cancel_keyboard())
        elif text == "❓ Помощь":
            send_message(chat_id, "/start - меню\n/me - мой ID", url, main_keyboard())
        elif text == "ℹ️ О боте":
            send_message(chat_id, "QR-бот v2.0\nВыбор цвета и формата", url, main_keyboard())
        else:
            send_message(chat_id, "Нажми «Создать QR-код»", url, main_keyboard())

def handle_location(chat_id, lat, lon, url):
    """Обработка геолокации. Возвращает адрес через Nominatim API."""
    geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        resp = requests.get(geo_url, headers={"User-Agent": "QRBot/1.0"}, timeout=30)
        if resp.status_code == 200:
            address = resp.json().get("display_name", "Адрес не найден")
            send_message(chat_id, f"Адрес: {address}", url)
        else:
            send_message(chat_id, "Ошибка определения адреса", url)
    except:
        send_message(chat_id, "Ошибка", url)