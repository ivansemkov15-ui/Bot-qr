import requests
import os

def generate_qr(text, format="png"):
    """
    Генерирует QR-код через API quickchart.io.
    Поддерживает форматы PNG и SVG.
    """
    os.makedirs("temp", exist_ok=True)
    url = f"https://quickchart.io/qr?text={text}&size=300&format={format}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            filename = f"temp/qr_{hash(text)}.{format}"
            with open(filename, "wb") as f:
                f.write(resp.content)
            return filename
    except Exception as e:
        print(f"Ошибка генерации QR: {e}")
    return None

def generate_colored_qr(text, color_hex="#000000"):
    """
    Генерирует цветной QR-код (только PNG).
    Цвет передаётся в формате HEX (например, #FF0000).
    """
    os.makedirs("temp", exist_ok=True)
    color = color_hex.lstrip("#")  # убираем # для API
    url = f"https://quickchart.io/qr?text={text}&size=300&dark={color}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            filename = f"temp/qr_color_{hash(text)}_{color}.png"
            with open(filename, "wb") as f:
                f.write(resp.content)
            return filename
    except Exception as e:
        print(f"Ошибка генерации цветного QR: {e}")
    return None