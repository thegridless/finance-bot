# -*- coding: utf-8 -*-
"""
Простая утилита для проверки доступа пользователей
"""

from config.settings import ALLOWED_USER_IDS


def is_user_allowed(user_id: int) -> bool:
    """
    Проверить, разрешен ли доступ пользователю
    
    Args:
        user_id (int): ID пользователя в Telegram
        
    Returns:
        bool: True если доступ разрешен, False если нет
    """
    return user_id in ALLOWED_USER_IDS


def check_access(message_or_call) -> bool:
    """
    Проверить доступ для сообщения или callback запроса
    
    Args:
        message_or_call: Объект Message или CallbackQuery
        
    Returns:
        bool: True если доступ разрешен, False если нет
    """
    user_id = None
    
    # Определяем тип объекта и извлекаем user_id
    if hasattr(message_or_call, 'from_user'):
        user_id = message_or_call.from_user.id
    elif hasattr(message_or_call, 'message') and message_or_call.message:
        user_id = message_or_call.message.from_user.id
    
    if not user_id:
        return False
    
    return is_user_allowed(user_id) 