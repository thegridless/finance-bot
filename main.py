# -*- coding: utf-8 -*-
"""
Главный файл для запуска финансового бота
"""

from bot.finance_bot import FinanceBot


def main():
    """Главная функция для запуска бота"""
    try:
        # Создаем экземпляр бота
        bot = FinanceBot()
        
        # Запускаем бота
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки. Завершение работы...")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    main() 