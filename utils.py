def format_money(amount):
    try:
        return f"{float(amount):,.0f} so'm".replace(",", " ")
    except:
        return "0 so'm"
import os
import sys

def resource_path(relative_path):
    """ Resurs yo'lini aniqlash (PyInstaller uchun) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
