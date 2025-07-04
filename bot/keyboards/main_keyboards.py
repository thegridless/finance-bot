# -*- coding: utf-8 -*-
"""
Основные клавиатуры для телеграм бота
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List
import pandas as pd


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню бота
    
    Returns:
        InlineKeyboardMarkup: Клавиатура главного меню
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("➕ Добавить трату", callback_data="add_expense"),
        InlineKeyboardButton("💰 Добавить доход", callback_data="add_income"),
        InlineKeyboardButton("📊 Статистика", callback_data="show_stats"),
        InlineKeyboardButton("📋 Мои транзакции", callback_data="show_transactions"),
        InlineKeyboardButton("🗑️ Удалить", callback_data="delete_transaction"),
        InlineKeyboardButton("⚙️ Управление", callback_data="show_management"),
    ]
    
    keyboard.add(*buttons[:2])  # Добавить трату и доход
    keyboard.add(*buttons[2:4])  # Статистика и транзакции
    keyboard.add(buttons[4])     # Удалить
    keyboard.add(buttons[5])     # Управление
    
    return keyboard


def get_transaction_type_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа транзакции
    
    Returns:
        InlineKeyboardMarkup: Клавиатура выбора типа
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("💸 Расходы", callback_data="type_expenses"),
        InlineKeyboardButton("💰 Доходы", callback_data="type_income")
    )
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    
    return keyboard


def get_categories_keyboard(categories: List[str], transaction_type: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора категории
    
    Args:
        categories (List[str]): Список категорий
        transaction_type (str): Тип транзакции для callback_data
    
    Returns:
        InlineKeyboardMarkup: Клавиатура выбора категории
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for category in categories:
        keyboard.add(
            InlineKeyboardButton(
                category, 
                callback_data=f"cat_{transaction_type}_{category}"
            )
        )
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    
    return keyboard


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения действия
    
    Args:
        action (str): Действие для callback_data
    
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_{action}")
    )
    
    return keyboard



def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора типа статистики
    
    Returns:
        InlineKeyboardMarkup: Клавиатура статистики
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🏷️ По категориям", callback_data="stats_categories"),
        InlineKeyboardButton("📋 Общая статистика", callback_data="stats_general")
    )
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    
    return keyboard


def get_period_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора периода статистики
    
    Returns:
        InlineKeyboardMarkup: Клавиатура периода
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("📅 Сегодня", callback_data="period_today"),
        InlineKeyboardButton("📅 Эта неделя", callback_data="period_week")
    )
    keyboard.add(
        InlineKeyboardButton("📅 Этот месяц", callback_data="period_month"),
        InlineKeyboardButton("📅 Этот год", callback_data="period_year")
    )
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_stats"))
    
    return keyboard


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой отмены
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура отмены
    """
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("❌ Отмена"))
    
    return keyboard


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопками пропуска и отмены
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура пропуска
    """
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(
        KeyboardButton("⏭️ Пропустить"),
        KeyboardButton("❌ Отмена")
    )
    
    return keyboard


def get_management_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для управления ботом
    
    Returns:
        InlineKeyboardMarkup: Клавиатура управления
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        InlineKeyboardButton("🔄 Обновить категории", callback_data="refresh_categories"),
        InlineKeyboardButton("📋 Информация о кеше", callback_data="cache_info")
    )
    keyboard.add(
        InlineKeyboardButton("🧹 Очистить кеш", callback_data="clear_cache"),
        InlineKeyboardButton("📊 Статус системы", callback_data="system_status")
    )
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    
    return keyboard


def get_transactions_list_keyboard(transactions_df: pd.DataFrame, action: str = "delete") -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора транзакции из списка для удаления
    
    Args:
        transactions_df (pd.DataFrame): DataFrame с транзакциями
        action (str): Действие - только "delete"
    
    Returns:
        InlineKeyboardMarkup: Клавиатура выбора транзакции
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    if transactions_df.empty:
        keyboard.add(InlineKeyboardButton("❌ Нет транзакций", callback_data="no_transactions"))
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
        return keyboard
    
    # Берем последние 10 транзакций и переворачиваем, чтобы новые были сверху
    recent_transactions = transactions_df.tail(10).iloc[::-1]
    
    for _, row in recent_transactions.iterrows():
        # Форматируем строку для кнопки
        emoji = "💸" if row['Тип'] == 'Расходы' else "💰"
        button_text = f"{emoji} {row['Дата']} - {row['Категория']} - {row['Сумма']}"
        
        # Обрезаем текст если он слишком длинный
        if len(button_text) > 50:
            button_text = button_text[:47] + "..."
        
        # Создаем callback_data с информацией о транзакции
        callback_data = f"{action}_trans_{row['Строка']}_{row['Тип'].lower()}"
        
        keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    
    return keyboard




def get_delete_confirmation_keyboard(transaction_row: int, transaction_type: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения удаления транзакции
    
    Args:
        transaction_row (int): Номер строки транзакции
        transaction_type (str): Тип транзакции
    
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения удаления
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    callback_data = f"confirm_delete_{transaction_row}_{transaction_type}"
    
    keyboard.add(
        InlineKeyboardButton("✅ Удалить", callback_data=callback_data),
        InlineKeyboardButton("❌ Отмена", callback_data="delete_transaction")
    )
    
    return keyboard 