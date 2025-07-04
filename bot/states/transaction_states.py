# -*- coding: utf-8 -*-
"""
Состояния для машины состояний при работе с транзакциями
"""
from telebot.handler_backends import State, StatesGroup


class TransactionStates(StatesGroup):
    """Состояния для добавления транзакций"""
    
    # Состояния для добавления новой транзакции
    choosing_type = State()  # Выбор типа транзакции (расходы/доходы)
    choosing_category = State()  # Выбор категории
    entering_amount = State()  # Ввод суммы
    entering_description = State()  # Ввод описания
    entering_date = State()  # Ввод даты (опционально)
    confirming = State()  # Подтверждение добавления
    

    
    # Состояния для удаления транзакции
    delete_choosing_transaction = State()  # Выбор транзакции для удаления
    delete_confirming = State()  # Подтверждение удаления
    
    # Состояния для просмотра статистики
    stats_choosing_period = State()  # Выбор периода для статистики
    stats_choosing_category = State()  # Выбор категории для статистики
    stats_choosing_type = State()  # Выбор типа графика


class MenuStates(StatesGroup):
    """Состояния для навигации по меню"""
    
    main_menu = State()  # Главное меню
    transaction_menu = State()  # Меню транзакций
    statistics_menu = State()  # Меню статистики
    settings_menu = State()  # Меню настроек 