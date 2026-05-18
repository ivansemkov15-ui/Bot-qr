# Reply-клавиатуры — кнопки, которые появляются под строкой ввода

def main_keyboard():
    """Главное меню бота"""
    return {
        "keyboard": [
            ["🔲 Создать QR-код"],
            ["❓ Помощь", "ℹ️ О боте"]
        ],
        "resize_keyboard": True  # автоматически подгоняет размер
    }

def color_keyboard():
    """Выбор цвета QR-кода"""
    return {
        "keyboard": [
            ["⚫ Черный", "🔴 Красный"],
            ["🔵 Синий", "🟢 Зеленый"],
            ["🟡 Желтый", "🟣 Фиолетовый"],
            ["🎨 Свой цвет (HEX)", "◀️ Назад"]
        ],
        "resize_keyboard": True
    }

def format_keyboard():
    """Выбор формата PNG/SVG"""
    return {
        "keyboard": [
            ["📱 PNG", "📄 SVG"],
            ["◀️ Назад"]
        ],
        "resize_keyboard": True
    }

def cancel_keyboard():
    """Клавиатура с кнопкой отмены диалога"""
    return {
        "keyboard": [["❌ Отмена"]],
        "resize_keyboard": True
    }

def back_keyboard():
    """Только кнопка назад"""
    return {
        "keyboard": [["◀️ Назад"]],
        "resize_keyboard": True
    }

def get_color_code(color_name):
    """Преобразует название цвета из кнопки в HEX-код"""
    colors = {
        "⚫ Черный": "#000000",
        "🔴 Красный": "#FF0000",
        "🔵 Синий": "#0000FF",
        "🟢 Зеленый": "#00FF00",
        "🟡 Желтый": "#FFFF00",
        "🟣 Фиолетовый": "#800080"
    }
    return colors.get(color_name, "#000000")