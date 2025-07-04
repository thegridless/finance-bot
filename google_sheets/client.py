# -*- coding: utf-8 -*-
"""
Клиент для работы с Google Sheets API
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import pandas as pd
from config.settings import GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_SPREADSHEET_ID
from utils.cache_manager import CacheManager


class GoogleSheetsClient:
    """Клиент для работы с Google Sheets"""
    
    def __init__(self):
        """Инициализация клиента Google Sheets"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = None
        self.client = None
        self.spreadsheet = None
        self.cache_manager = CacheManager()
        self._authenticate()
    
    def _authenticate(self):
        """Аутентификация с помощью Service Account"""
        try:
            self.credentials = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_PATH, 
                scopes=self.scope
            )
            self.client = gspread.authorize(self.credentials)
            self.spreadsheet = self.client.open_by_key(GOOGLE_SHEETS_SPREADSHEET_ID)
            print("✅ Успешно подключен к Google Sheets")
        except Exception as e:
            print(f"❌ Ошибка подключения к Google Sheets: {e}")
            raise
    
    def get_worksheet(self, sheet_name: str = None):
        """
        Получить лист таблицы
        
        Args:
            sheet_name (str): Название листа. Если None, возвращает первый лист
        
        Returns:
            gspread.Worksheet: Объект листа
        """
        try:
            if sheet_name:
                return self.spreadsheet.worksheet(sheet_name)
            else:
                return self.spreadsheet.sheet1
        except Exception as e:
            print(f"❌ Ошибка получения листа {sheet_name}: {e}")
            raise
    
    def get_all_data(self, sheet_name: str = None) -> List[List[str]]:
        """
        Получить все данные из листа
        
        Args:
            sheet_name (str): Название листа
        
        Returns:
            List[List[str]]: Все данные из листа
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            return worksheet.get_all_values()
        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            raise
    
    def get_categories(self, category_type: str = "расходы") -> List[str]:
        """
        Получить список категорий (с использованием кеша)
        
        Args:
            category_type (str): Тип категорий - "расходы" или "доходы"
        
        Returns:
            List[str]: Список категорий
        """
        try:
            # Сначала пытаемся загрузить из кеша
            cached_categories = self.cache_manager.load_categories()
            
            if cached_categories and category_type in cached_categories:
                print(f"📋 Загружены категории из кеша: {category_type}")
                return cached_categories[category_type]
            
            # Если кеш пуст или устарел, загружаем из Google Sheets
            print(f"🔄 Загружаем категории из Google Sheets...")
            categories = self._fetch_categories_from_sheets(category_type)
            
            # Обновляем кеш
            self._update_cache_with_categories()
            
            return categories
        except Exception as e:
            print(f"❌ Ошибка получения категорий: {e}")
            return []
    
    def _fetch_categories_from_sheets(self, category_type: str = "расходы") -> List[str]:
        """
        Получить список категорий напрямую из Google Sheets
        
        Args:
            category_type (str): Тип категорий - "расходы" или "доходы"
        
        Returns:
            List[str]: Список категорий
        """
        try:
            data = self.get_all_data('Сводка')
            if not data:
                return []
            
            categories = []
            
            # Ищем строку "Итого" - после неё идут категории
            start_index = -1
            for i, row in enumerate(data):
                if len(row) > 1 and row[1] == "Итого":
                    start_index = i + 1  # Начинаем с следующей строки после "Итого"
                    break
            
            if start_index == -1:
                print("❌ Не найдена строка 'Итого' в листе Сводка")
                return []
            
            # Определяем индекс столбца для нужного типа категорий
            if category_type.lower() == "расходы":
                column_index = 1  # Столбец B (индекс 1)
            elif category_type.lower() == "доходы":
                column_index = 7  # Столбец H (индекс 7)
            else:
                return []
            
            # Собираем категории начиная с найденной позиции
            for i in range(start_index, len(data)):
                row = data[i]
                if len(row) > column_index and row[column_index]:
                    category = row[column_index].strip()
                    
                    # Пропускаем пустые и служебные строки
                    if category and category not in ["Итого", "Предполагаемые", "Фактические"]:
                        # Очищаем от спецсимволов (например \xa0)
                        category = category.replace('\xa0', ' ').strip()
                        categories.append(category)
                
                # Останавливаемся, если дошли до конца данных
                if i >= len(data) - 1:
                    break
            
            return categories
        except Exception as e:
            print(f"❌ Ошибка получения категорий: {e}")
            return []
    
    def _update_cache_with_categories(self):
        """Обновить кеш всеми категориями"""
        try:
            categories = {
                "расходы": self._fetch_categories_from_sheets("расходы"),
                "доходы": self._fetch_categories_from_sheets("доходы")
            }
            
            self.cache_manager.save_categories(categories)
            print("✅ Кеш категорий обновлен")
        except Exception as e:
            print(f"❌ Ошибка обновления кеша: {e}")
    
    def refresh_categories_cache(self) -> Dict[str, Any]:
        """
        Принудительно обновить кеш категорий
        
        Returns:
            Dict[str, Any]: Результат обновления
        """
        try:
            # Очищаем старый кеш
            self.cache_manager.clear_cache()
            
            # Загружаем категории из Google Sheets
            expenses = self._fetch_categories_from_sheets("расходы")
            income = self._fetch_categories_from_sheets("доходы")
            
            # Сохраняем в кеш
            categories = {
                "расходы": expenses,
                "доходы": income
            }
            
            success = self.cache_manager.save_categories(categories)
            
            return {
                'success': success,
                'expenses_count': len(expenses),
                'income_count': len(income),
                'total_categories': len(expenses) + len(income)
            }
        except Exception as e:
            print(f"❌ Ошибка обновления кеша: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Получить информацию о кеше категорий
        
        Returns:
            Dict[str, Any]: Информация о кеше
        """
        return self.cache_manager.get_cache_info()
    
    def add_transaction(self, transaction_type: str, date: str, amount: float, description: str, category: str):
        """
        Добавить транзакцию в таблицу
        
        Args:
            transaction_type (str): Тип транзакции - "расходы" или "доходы"
            date (str): Дата в формате 'DD.MM.YYYY'
            amount (float): Сумма как число
            description (str): Описание транзакции
            category (str): Категория транзакции
        """
        try:
            worksheet = self.get_worksheet('Транзакции')
            
            # Находим первую пустую строку для добавления данных
            data = worksheet.get_all_values()
            empty_row = len(data) + 1
            
            if transaction_type.lower() == "расходы":
                # Добавляем в секцию расходов (столбцы B-E)
                range_name = f'B{empty_row}:E{empty_row}'
                worksheet.update(range_name, [[date, amount, description, category]])
                print(f"✅ Расход добавлен: {date} - {category} - {amount}")
            
            elif transaction_type.lower() == "доходы":
                # Добавляем в секцию доходов (столбцы G-J)
                range_name = f'G{empty_row}:J{empty_row}'
                worksheet.update(range_name, [[date, amount, description, category]])
                print(f"✅ Доход добавлен: {date} - {category} - {amount}")
            
            else:
                raise ValueError(f"Неподдерживаемый тип транзакции: {transaction_type}")
                
        except Exception as e:
            print(f"❌ Ошибка добавления транзакции: {e}")
            raise
    
    def get_transactions_df(self, transaction_type: str = "все") -> pd.DataFrame:
        """
        Получить данные о транзакциях в виде DataFrame
        
        Args:
            transaction_type (str): Тип транзакций - "расходы", "доходы" или "все"
        
        Returns:
            pd.DataFrame: DataFrame с данными о транзакциях
        """
        try:
            data = self.get_all_data('Транзакции')
            if not data:
                return pd.DataFrame()
            
            transactions = []
            
            # Обрабатываем данные начиная с 5-й строки (индекс 4)
            for i, row in enumerate(data[4:], start=5):
                # Проверяем расходы (столбцы B-E, индексы 1-4)
                if (transaction_type.lower() in ["расходы", "все"] and 
                    len(row) > 4 and row[1] and row[2] and row[4]):
                    transactions.append({
                        'Тип': 'Расходы',
                        'Дата': row[1],
                        'Сумма': row[2],
                        'Описание': row[3],
                        'Категория': row[4],
                        'Строка': i
                    })
                
                # Проверяем доходы (столбцы G-J, индексы 6-9)
                if (transaction_type.lower() in ["доходы", "все"] and 
                    len(row) > 9 and row[6] and row[7] and row[9]):
                    transactions.append({
                        'Тип': 'Доходы',
                        'Дата': row[6],
                        'Сумма': row[7],
                        'Описание': row[8],
                        'Категория': row[9],
                        'Строка': i
                    })
            
            df = pd.DataFrame(transactions)
            
            if not df.empty:
                # Очистка и преобразование данных
                df['Сумма_числовая'] = df['Сумма'].apply(self._parse_amount)
                df['Дата_datetime'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y', errors='coerce')
            
            return df
        except Exception as e:
            print(f"❌ Ошибка получения DataFrame: {e}")
            return pd.DataFrame()
    
    def _parse_amount(self, amount_str: str) -> float:
        """
        Преобразовать строку суммы в число
        
        Args:
            amount_str (str): Строка с суммой (например, "1000,00 р.")
        
        Returns:
            float: Числовое значение суммы
        """
        try:
            # Убираем символ валюты и заменяем запятую на точку
            amount_clean = amount_str.replace('р.', '').replace(' ', '').replace(',', '.')
            return float(amount_clean)
        except:
            return 0.0
    
    def update_transaction(self, row_index: int, transaction_type: str, date: str, amount: float, description: str, category: str):
        """
        Обновить существующую транзакцию
        
        Args:
            row_index (int): Индекс строки для обновления (начиная с 1)
            transaction_type (str): Тип транзакции - "расходы" или "доходы"
            date (str): Дата
            amount (float): Сумма как число
            description (str): Описание
            category (str): Категория
        """
        try:
            worksheet = self.get_worksheet('Транзакции')
            
            if transaction_type.lower() == "расходы":
                # Обновляем секцию расходов (столбцы B-E)
                range_name = f'B{row_index}:E{row_index}'
                worksheet.update(range_name, [[date, amount, description, category]])
                print(f"✅ Расход обновлен в строке {row_index}")
            
            elif transaction_type.lower() == "доходы":
                # Обновляем секцию доходов (столбцы G-J)
                range_name = f'G{row_index}:J{row_index}'
                worksheet.update(range_name, [[date, amount, description, category]])
                print(f"✅ Доход обновлен в строке {row_index}")
            
            else:
                raise ValueError(f"Неподдерживаемый тип транзакции: {transaction_type}")
                
        except Exception as e:
            print(f"❌ Ошибка обновления транзакции: {e}")
            raise
    
    def delete_transaction(self, row_index: int, transaction_type: str):
        """
        Удалить транзакцию (очистить соответствующие ячейки)
        
        Args:
            row_index (int): Индекс строки для удаления (начиная с 1)
            transaction_type (str): Тип транзакции - "расходы" или "доходы"
        """
        try:
            worksheet = self.get_worksheet('Транзакции')
            
            if transaction_type.lower() == "расходы":
                # Очищаем секцию расходов (столбцы B-E)
                range_name = f'B{row_index}:E{row_index}'
                worksheet.batch_clear([range_name])
                print(f"✅ Расход удален из строки {row_index}")
            
            elif transaction_type.lower() == "доходы":
                # Очищаем секцию доходов (столбцы G-J)
                range_name = f'G{row_index}:J{row_index}'
                worksheet.batch_clear([range_name])
                print(f"✅ Доход удален из строки {row_index}")
            
            else:
                raise ValueError(f"Неподдерживаемый тип транзакции: {transaction_type}")
                
        except Exception as e:
            print(f"❌ Ошибка удаления транзакции: {e}")
            raise 