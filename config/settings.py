# -*- coding: utf-8 -*-
"""
Настройки проекта
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Настройки Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Настройки Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH = 'google_service_account.json'
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')

# Настройки таблицы
SHEET_NAME = 'Лист1'  # Название листа в Google Sheets
CATEGORIES_RANGE = 'A:A'  # Диапазон для категорий
DATA_RANGE = 'A:D'  # Диапазон для данных (дата, категория, сумма, описание)

# Настройки графиков
CHART_WIDTH = 10
CHART_HEIGHT = 6
CHART_DPI = 300 

# Настройки доступа
ALLOWED_USER_IDS = [535511089, 47 6410829]  # Список разрешенных пользователей (добавлять новые ID сюда) 