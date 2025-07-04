# -*- coding: utf-8 -*-
"""
Модель данных для транзакций
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Transaction:
    """Модель транзакции"""
    
    transaction_type: str  # "расходы" или "доходы"
    date: str  # Дата в формате DD.MM.YYYY
    amount: float  # Сумма как число
    description: str  # Описание транзакции
    category: str  # Категория транзакции
    row_index: Optional[int] = None  # Индекс строки в таблице (для редактирования)
    
    def __post_init__(self):
        """Валидация данных после создания объекта"""
        if self.transaction_type.lower() not in ["расходы", "доходы"]:
            raise ValueError(f"Неподдерживаемый тип транзакции: {self.transaction_type}")
        
        # Проверяем формат даты
        try:
            datetime.strptime(self.date, "%d.%m.%Y")
        except ValueError:
            raise ValueError(f"Неверный формат даты: {self.date}. Ожидается DD.MM.YYYY")
    
    def get_amount_float(self) -> float:
        """
        Получить сумму в виде числа
        
        Returns:
            float: Числовое значение суммы
        """
        return self.amount
    
    def format_for_display(self) -> str:
        """
        Форматировать транзакцию для отображения
        
        Returns:
            str: Отформатированная строка
        """
        type_emoji = "💸" if self.transaction_type.lower() == "расходы" else "💰"
        
        # Форматируем сумму для отображения
        amount_display = f"{self.amount:,.2f} р.".replace('.', ',')
        
        return f"{type_emoji} {self.date} | {amount_display} | {self.category}\n📝 {self.description}"
    
    def to_dict(self) -> dict:
        """
        Преобразовать в словарь
        
        Returns:
            dict: Словарь с данными транзакции
        """
        return {
            'type': self.transaction_type,
            'date': self.date,
            'amount': self.amount,
            'description': self.description,
            'category': self.category,
            'row_index': self.row_index
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """
        Создать объект из словаря
        
        Args:
            data (dict): Словарь с данными транзакции
        
        Returns:
            Transaction: Объект транзакции
        """
        return cls(
            transaction_type=data['type'],
            date=data['date'],
            amount=data['amount'],
            description=data['description'],
            category=data['category'],
            row_index=data.get('row_index')
        ) 