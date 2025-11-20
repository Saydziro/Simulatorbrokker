# data_manager.py
import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from models import Portfolio, Market

USERS_DIR = "users"

def ensure_users_dir():
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

def get_user_folder(username: str) -> str:
    return os.path.join(USERS_DIR, username)

def get_data_file(username: str) -> str:
    return os.path.join(get_user_folder(username), "portfolio_data.json")

def select_or_create_user() -> str:
    ensure_users_dir()
    existing_users = [d for d in os.listdir(USERS_DIR) if os.path.isdir(os.path.join(USERS_DIR, d))]
    
    root = tk.Tk()
    root.withdraw()  # скрыть главное окно
    
    if existing_users:
        user_list = "\n".join(f"- {u}" for u in existing_users)
        prompt = f"Выберите пользователя или введите новое имя:\n\nСуществующие:\n{user_list}"
    else:
        prompt = "Введите имя нового пользователя:"
    
    while True:
        username = simpledialog.askstring("Пользователь", prompt, parent=root)
        if username is None:
            exit()  # пользователь нажал Отмена
        username = username.strip()
        if username:
            break
        messagebox.showwarning("Ошибка", "Имя не может быть пустым.")
    
    # Создаём папку пользователя, если новая
    user_folder = get_user_folder(username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    root.destroy()
    return username

def save_data(username: str, portfolio: Portfolio, market: Market):
    data_file = get_data_file(username)
    data = {
        "portfolio": portfolio.to_dict(),
        "market": market.to_dict()
    }
    temp_file = data_file + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, data_file)
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise e

def load_data(username: str):
    data_file = get_data_file(username)
    if not os.path.exists(data_file) or os.path.getsize(data_file) == 0:
        return Portfolio(), Market()

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "portfolio" in data and "market" in data:
            portfolio = Portfolio.from_dict(data["portfolio"])
            market = Market(data["market"])
            return portfolio, market
        else:
            raise ValueError("Неверная структура файла")
    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        # Возвращаем новые данные при ошибке
        return Portfolio(), Market()
