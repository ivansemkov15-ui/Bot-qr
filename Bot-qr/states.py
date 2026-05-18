# Простая реализация FSM (конечного автомата) на словаре
# Нужна для пошагового диалога: текст -->цвет --> формат

user_states = {}

# ID состояний
STATE_IDLE = 0               # не в диалоге
STATE_WAITING_QR_TEXT = 1    # ждём текст
STATE_WAITING_QR_COLOR = 2   # ждём цвет
STATE_WAITING_QR_FORMAT = 3  # ждём формат

# Временное хранилище данных пользователя в диалоге
user_temp_data = {}

def get_state(chat_id):
    return user_states.get(chat_id, STATE_IDLE)

def set_state(chat_id, state):
    user_states[chat_id] = state

def clear_state(chat_id):
    """Полностью сбрасывает состояние пользователя"""
    user_states[chat_id] = STATE_IDLE
    if chat_id in user_temp_data:
        del user_temp_data[chat_id]

def set_temp(chat_id, key, value):
    if chat_id not in user_temp_data:
        user_temp_data[chat_id] = {}
    user_temp_data[chat_id][key] = value

def get_temp(chat_id, key):
    return user_temp_data.get(chat_id, {}).get(key)