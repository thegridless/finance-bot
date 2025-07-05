# -*- coding: utf-8 -*-
"""
Основной класс финансового бота
"""
import telebot
from telebot.storage import StateMemoryStorage
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from typing import Dict, Any

from config.settings import TELEGRAM_BOT_TOKEN
from google_sheets.client import GoogleSheetsClient
from bot.keyboards.main_keyboards import (
    get_main_menu_keyboard,
    get_categories_keyboard,
    get_confirmation_keyboard,
    get_cancel_keyboard,
    get_skip_keyboard,
    get_statistics_keyboard,
    get_management_keyboard,
    get_transactions_list_keyboard,
    get_delete_confirmation_keyboard
)
from bot.states.transaction_states import TransactionStates, MenuStates
from models.transaction import Transaction
from utils.access_checker import check_access


class FinanceBot:
    """Основной класс финансового бота"""
    
    def __init__(self):
        """Инициализация бота"""
        self.state_storage = StateMemoryStorage()
        self.bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, state_storage=self.state_storage)
        self.user_data: Dict[int, Dict[str, Any]] = {}
        self.sheets_client = GoogleSheetsClient()
        
        # Регистрируем обработчики
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация всех обработчиков"""
        
        # Команды
        self.bot.message_handler(commands=['start', 'help'])(self.send_welcome)
        self.bot.message_handler(commands=['menu'])(self.show_main_menu)
        
        # Callback обработчики
        self.bot.callback_query_handler(func=lambda call: call.data in ['add_expense', 'add_income'])(self.handle_add_transaction)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))(self.handle_category_selection)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_') and not call.data.startswith('confirm_delete_') and not call.data.startswith('confirm_edit_'))(self.handle_confirmation)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_'))(self.handle_cancellation)
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')(self.handle_back_to_main)
        
        # Статистика и транзакции
        self.bot.callback_query_handler(func=lambda call: call.data == 'show_stats')(self.handle_show_stats)
        self.bot.callback_query_handler(func=lambda call: call.data == 'show_transactions')(self.handle_show_transactions)

        self.bot.callback_query_handler(func=lambda call: call.data == 'delete_transaction')(self.handle_delete_transaction)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('stats_'))(self.handle_stats_type)
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_stats')(self.handle_back_to_stats)
        
        # Управление
        self.bot.callback_query_handler(func=lambda call: call.data == 'show_management')(self.handle_show_management)
        self.bot.callback_query_handler(func=lambda call: call.data == 'refresh_categories')(self.handle_refresh_categories)
        self.bot.callback_query_handler(func=lambda call: call.data == 'cache_info')(self.handle_cache_info)
        self.bot.callback_query_handler(func=lambda call: call.data == 'clear_cache')(self.handle_clear_cache)
        self.bot.callback_query_handler(func=lambda call: call.data == 'system_status')(self.handle_system_status)
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_management')(self.handle_back_to_management)
        
        # Удаление транзакций
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete_trans_'))(self.handle_delete_transaction_selection)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))(self.handle_confirm_delete_transaction)
        

        
        # Главный обработчик сообщений
        self.bot.message_handler(func=lambda message: True)(self.handle_all_messages)
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Получить данные пользователя
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            Dict[str, Any]: Данные пользователя
        """
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        return self.user_data[user_id]
    
    def clear_user_data(self, user_id: int):
        """
        Очистить данные пользователя
        
        Args:
            user_id (int): ID пользователя
        """
        if user_id in self.user_data:
            self.user_data[user_id].clear()
    
    def send_welcome(self, message: Message):
        """Обработчик команд /start и /help"""
        try:
            # Проверяем доступ пользователя
            if not check_access(message):
                self.bot.send_message(
                    message.chat.id,
                    "🚫 У вас нет доступа к этому боту.\n\n"
                    "Для получения доступа обратитесь к администратору."
                )
                return
            
            welcome_text = """
🏦 *Добро пожаловать в Финансовый Бот!*

Я помогу вам вести учет доходов и расходов в Google Sheets.

*Основные функции:*
• ➕ Добавление трат и доходов
• ✏️ Редактирование транзакций
• 🗑️ Удаление записей
• 📊 Статистика и графики
• 📋 Просмотр истории транзакций

Нажмите на кнопку ниже, чтобы начать!
            """
            
            self.bot.send_message(
                message.chat.id,
                welcome_text,
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard()
            )
            
            # Устанавливаем состояние главного меню
            self.bot.set_state(message.from_user.id, MenuStates.main_menu, message.chat.id)
            
        except Exception as e:
            self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")
    
    def show_main_menu(self, message: Message):
        """Показать главное меню"""
        try:
            # Проверяем доступ пользователя
            if not check_access(message):
                self.bot.send_message(
                    message.chat.id,
                    "🚫 У вас нет доступа к этому боту.\n\n"
                    "Для получения доступа обратитесь к администратору."
                )
                return
            
            # Очищаем данные пользователя и состояния
            self.clear_user_data(message.from_user.id)
            
            self.bot.send_message(
                message.chat.id,
                "🏦 *Главное меню*\n\nВыберите действие:",
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard()
            )
            
            self.bot.set_state(message.from_user.id, MenuStates.main_menu, message.chat.id)
            
        except Exception as e:
            self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")
    
    def handle_add_transaction(self, call: CallbackQuery):
        """Обработчик для добавления транзакции"""
        try:
            # Проверяем доступ пользователя
            if not check_access(call):
                self.bot.answer_callback_query(call.id, "🚫 У вас нет доступа к этому боту.")
                return
            
            transaction_type = "расходы" if call.data == "add_expense" else "доходы"
            
            # Сохраняем тип транзакции
            user_session = self.get_user_data(call.from_user.id)
            user_session['transaction_type'] = transaction_type
            
            # Получаем категории
            categories = self.sheets_client.get_categories(transaction_type)
            
            if not categories:
                self.bot.edit_message_text(
                    f"❌ Категории {transaction_type} не найдены. Проверьте настройки таблицы.",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            # Показываем клавиатуру с категориями
            type_text = "💸 расходы" if transaction_type == "расходы" else "💰 доходы"
            self.bot.edit_message_text(
                f"Выберите категорию для {type_text}:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=get_categories_keyboard(categories, transaction_type)
            )
            
            # Устанавливаем состояние выбора категории
            self.bot.set_state(call.from_user.id, TransactionStates.choosing_category, call.message.chat.id)
            
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_category_selection(self, call: CallbackQuery):
        """Обработчик выбора категории"""
        try:
            # Парсим callback_data: cat_расходы_Питание
            parts = call.data.split('_', 2)
            if len(parts) != 3:
                self.bot.answer_callback_query(call.id, "❌ Ошибка данных")
                return
            
            _, transaction_type, category = parts
            
            # Сохраняем категорию
            user_session = self.get_user_data(call.from_user.id)
            user_session['category'] = category
            
            # Подтверждаем выбор категории
            self.bot.edit_message_text(
                f"✅ Выбрана категория: {category}",
                call.message.chat.id,
                call.message.message_id
            )
            
            # Отправляем новое сообщение для ввода суммы
            self.bot.send_message(
                call.message.chat.id,
                f"💰 Введите сумму для категории '{category}':\n\n"
                f"Примеры: 150, 1500.50, 100,25",
                reply_markup=get_cancel_keyboard()
            )
            
            # Устанавливаем состояние ввода суммы
            self.bot.set_state(call.from_user.id, TransactionStates.entering_amount, call.message.chat.id)
            
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_all_messages(self, message: Message):
        """Обработчик всех сообщений с проверкой состояний"""
        # Проверяем доступ пользователя
        if not check_access(message):
            self.bot.send_message(
                message.chat.id,
                "🚫 У вас нет доступа к этому боту.\n\n"
                "Для получения доступа обратитесь к администратору."
            )
            return
        
        user_state = self.bot.get_state(message.from_user.id, message.chat.id)
        
        try:
            # Проверяем состояние ввода суммы
            if user_state == "TransactionStates:entering_amount":
                self.handle_amount_input_manual(message)
                return
            
            # Проверяем состояние ввода описания
            if user_state == "TransactionStates:entering_description":
                self.handle_description_input_manual(message)
                return
            

            
            # Если состояние подтверждения - игнорируем текстовые сообщения
            if user_state == "TransactionStates:confirming":
                self.bot.send_message(
                    message.chat.id,
                    "⏳ Ожидается подтверждение транзакции. Используйте кнопки выше."
                )
                return
            

            
            # Если состояние не установлено или неизвестно
            self.bot.send_message(
                message.chat.id,
                "❓ Не понимаю эту команду. Используйте /menu для возврата в главное меню.",
                reply_markup=get_main_menu_keyboard()
            )
            
        except Exception as e:
            self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")
    
    def handle_amount_input_manual(self, message: Message):
        """Ручной обработчик ввода суммы"""
        try:
            # Проверяем на отмену
            if message.text == "❌ Отмена":
                # Убираем клавиатуру и показываем главное меню
                self.bot.send_message(
                    message.chat.id,
                    "❌ Действие отменено",
                    reply_markup=ReplyKeyboardRemove()
                )
                self.show_main_menu(message)
                return
            
            # Валидируем сумму
            amount_text = message.text.replace(',', '.')
            try:
                amount_float = float(amount_text)
                if amount_float <= 0:
                    raise ValueError("Сумма должна быть положительной")
            except ValueError:
                self.bot.send_message(
                    message.chat.id,
                    "❌ Неверный формат суммы. Введите число больше 0.\n\n"
                    "Примеры: 150, 1500.50, 100,25",
                    reply_markup=get_cancel_keyboard()
                )
                return
            
            # Сохраняем сумму как число
            user_session = self.get_user_data(message.from_user.id)
            user_session['amount'] = amount_float
            
            # Убираем предыдущую клавиатуру и запрашиваем описание
            self.bot.send_message(
                message.chat.id,
                "✅ Сумма принята",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Запрашиваем описание
            self.bot.send_message(
                message.chat.id,
                "📝 Введите описание транзакции:",
                reply_markup=get_skip_keyboard()
            )
            
            # Устанавливаем состояние ввода описания
            self.bot.set_state(message.from_user.id, TransactionStates.entering_description, message.chat.id)
            
        except Exception as e:
            self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")
    
    def handle_description_input_manual(self, message: Message):
        """Ручной обработчик ввода описания"""
        try:
            # Проверяем на отмену
            if message.text == "❌ Отмена":
                # Убираем клавиатуру и показываем главное меню
                self.bot.send_message(
                    message.chat.id,
                    "❌ Действие отменено",
                    reply_markup=ReplyKeyboardRemove()
                )
                self.show_main_menu(message)
                return
            
            # Сохраняем описание
            user_session = self.get_user_data(message.from_user.id)
            description = "Без описания" if message.text == "⏭️ Пропустить" else message.text
            user_session['description'] = description
            
            # Устанавливаем текущую дату
            current_date = datetime.now().strftime("%d.%m.%Y")
            user_session['date'] = current_date
            
            # Показываем подтверждение
            transaction = Transaction(
                transaction_type=user_session['transaction_type'],
                date=user_session['date'],
                amount=user_session['amount'],
                description=user_session['description'],
                category=user_session['category']
            )
            
            confirmation_text = f"""
📋 *Подтверждение транзакции*

{transaction.format_for_display()}

Добавить эту транзакцию?
            """
            
            # Убираем reply клавиатуру
            self.bot.send_message(
                message.chat.id,
                "✅ Данные приняты",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Показываем подтверждение с inline клавиатурой
            self.bot.send_message(
                message.chat.id,
                confirmation_text,
                parse_mode='Markdown',
                reply_markup=get_confirmation_keyboard('add')
            )
            
            # Устанавливаем состояние подтверждения
            self.bot.set_state(message.from_user.id, TransactionStates.confirming, message.chat.id)
            
        except Exception as e:
            self.bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")
    
    def handle_confirmation(self, call: CallbackQuery):
        """Обработчик подтверждения действий"""
        try:
            action = call.data.split('_', 1)[1]
            
            if action == 'add':
                # Добавляем транзакцию
                user_session = self.get_user_data(call.from_user.id)
                
                # Создаем объект транзакции
                transaction = Transaction(
                    transaction_type=user_session['transaction_type'],
                    date=user_session['date'],
                    amount=user_session['amount'],
                    description=user_session['description'],
                    category=user_session['category']
                )
                
                # Добавляем в Google Sheets
                try:
                    self.sheets_client.add_transaction(
                        transaction_type=transaction.transaction_type,
                        date=transaction.date,
                        amount=transaction.amount,
                        description=transaction.description,
                        category=transaction.category
                    )
                    
                    self.bot.edit_message_text(
                        "✅ Транзакция успешно добавлена!",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    
                    # Показываем главное меню
                    self.bot.send_message(
                        call.message.chat.id,
                        "🏦 *Главное меню*\n\nВыберите действие:",
                        parse_mode='Markdown',
                        reply_markup=get_main_menu_keyboard()
                    )
                    
                except Exception as e:
                    self.bot.edit_message_text(
                        f"❌ Ошибка добавления транзакции: {e}",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    
                    # Показываем главное меню
                    self.bot.send_message(
                        call.message.chat.id,
                        "🏦 *Главное меню*\n\nВыберите действие:",
                        parse_mode='Markdown',
                        reply_markup=get_main_menu_keyboard()
                    )
                
                # Очищаем данные пользователя
                self.clear_user_data(call.from_user.id)
                
            # Очищаем состояние
            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_cancellation(self, call: CallbackQuery):
        """Обработчик отмены действий"""
        try:
            self.bot.edit_message_text(
                "❌ Действие отменено",
                call.message.chat.id,
                call.message.message_id
            )
            
            # Показываем главное меню
            self.bot.send_message(
                call.message.chat.id,
                "🏦 *Главное меню*\n\nВыберите действие:",
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard()
            )
            
            # Очищаем данные пользователя
            self.clear_user_data(call.from_user.id)
            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_back_to_main(self, call: CallbackQuery):
        """Обработчик возврата в главное меню"""
        try:
            self.bot.edit_message_text(
                "🏦 *Главное меню*\n\nВыберите действие:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard()
            )
            
            # Очищаем данные пользователя
            self.clear_user_data(call.from_user.id)
            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    # Обработчики для статистики и транзакций
    def handle_show_stats(self, call: CallbackQuery):
        """Обработчик показа статистики"""
        try:
            # Проверяем доступ пользователя
            if not check_access(call):
                self.bot.answer_callback_query(call.id, "🚫 У вас нет доступа к этому боту.")
                return
            
            self.bot.edit_message_text(
                "📊 *Статистика*\n\nВыберите тип статистики:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_statistics_keyboard()
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_show_transactions(self, call: CallbackQuery):
        """Обработчик показа транзакций"""
        try:
            # Получаем последние 10 транзакций
            df = self.sheets_client.get_transactions_df("все")
            
            if df.empty:
                self.bot.edit_message_text(
                    "📋 *Мои транзакции*\n\n❌ Транзакции не найдены",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                    )
                )
            else:
                # Берем последние 10 транзакций
                recent_transactions = df.tail(10)
                
                text = "📋 *Последние транзакции*\n\n"
                for _, row in recent_transactions.iterrows():
                    emoji = "💸" if row['Тип'] == 'Расходы' else "💰"
                    text += f"{emoji} {row['Дата']} - {row['Категория']}\n"
                    text += f"   {row['Сумма']} - {row['Описание']}\n\n"
                
                self.bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                    )
                )
            
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    

    
    def handle_delete_transaction(self, call: CallbackQuery):
        """Обработчик удаления транзакции"""
        try:
            # Получаем последние транзакции
            df = self.sheets_client.get_transactions_df("все")
            
            if df.empty:
                self.bot.edit_message_text(
                    "🗑️ *Удаление транзакции*\n\n❌ Транзакции не найдены",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                    )
                )
            else:
                # Показываем список транзакций для удаления
                self.bot.edit_message_text(
                    "🗑️ *Удаление транзакции*\n\nВыберите транзакцию для удаления:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=get_transactions_list_keyboard(df, "delete")
                )
            
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_stats_type(self, call: CallbackQuery):
        """Обработчик типов статистики"""
        try:
            stats_type = call.data.split('_')[1]
            
            if stats_type == 'categories':
                # Статистика по категориям
                df = self.sheets_client.get_transactions_df("все")
                
                if df.empty:
                    text = "📊 *Статистика по категориям*\n\n❌ Данные не найдены"
                else:
                    # Группируем по категориям
                    category_stats = df.groupby('Категория')['Сумма_числовая'].sum().sort_values(ascending=False)
                    
                    text = "📊 *Статистика по категориям*\n\n"
                    for category, amount in category_stats.head(10).items():
                        text += f"🏷️ {category}: {amount:,.2f} р. \n"
            
            elif stats_type == 'general':
                # Общая статистика
                df = self.sheets_client.get_transactions_df("все")
                
                if df.empty:
                    text = "📋 *Общая статистика*\n\n❌ Данные не найдены"
                else:
                    total_expense = df[df['Тип'] == 'Расходы']['Сумма_числовая'].sum()
                    total_income = df[df['Тип'] == 'Доходы']['Сумма_числовая'].sum()
                    balance = total_income - total_expense
                    
                    text = f"""📋 *Общая статистика*

💸 Всего расходов: {total_expense:,.2f} р.
💰 Всего доходов: {total_income:,.2f} р.
🏦 Баланс: {balance:,.2f} р.

📊 Количество транзакций: {len(df)}"""
            
            else:
                text = f"📊 *Статистика*\n\nФункция '{stats_type}' в разработке"
            
            self.bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("🔙 Назад", callback_data="show_stats")
                )
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_back_to_stats(self, call: CallbackQuery):
        """Обработчик возврата к статистике"""
        try:
            self.bot.edit_message_text(
                "📊 *Статистика*\n\nВыберите тип статистики:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_statistics_keyboard()
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    # Обработчики для управления
    def handle_show_management(self, call: CallbackQuery):
        """Обработчик показа управления"""
        try:
            # Проверяем доступ пользователя
            if not check_access(call):
                self.bot.answer_callback_query(call.id, "🚫 У вас нет доступа к этому боту.")
                return
            
            self.bot.edit_message_text(
                "⚙️ *Управление ботом*\n\nВыберите действие:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_management_keyboard()
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_refresh_categories(self, call: CallbackQuery):
        """Обработчик обновления категорий"""
        try:
            # Показываем индикатор загрузки
            self.bot.edit_message_text(
                "🔄 *Обновление категорий*\n\n⏳ Загружаем категории из Google Sheets...",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
            # Обновляем кеш
            result = self.sheets_client.refresh_categories_cache()
            
            if result['success']:
                text = f"""✅ *Категории обновлены!*

📊 Статистика обновления:
• 💸 Расходы: {result['expenses_count']} категорий
• 💰 Доходы: {result['income_count']} категорий
• 📋 Всего: {result['total_categories']} категорий"""
            else:
                text = f"❌ *Ошибка обновления*\n\n{result.get('error', 'Неизвестная ошибка')}"
            
            self.bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_management")
                )
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_cache_info(self, call: CallbackQuery):
        """Обработчик информации о кеше"""
        try:
            cache_info = self.sheets_client.get_cache_info()
            
            if cache_info['exists']:
                if 'error' in cache_info:
                    text = f"❌ *Ошибка кеша*\n\n{cache_info['error']}"
                elif 'message' in cache_info:
                    text = f"⚠️ *Информация о кеше*\n\n{cache_info['message']}"
                    if 'total_categories' in cache_info:
                        text += f"\n📋 Категорий в кеше: {cache_info['total_categories']}"
                else:
                    status = "🔴 Истек" if cache_info['is_expired'] else "🟢 Действительный"
                    age_hours = cache_info['age_hours']
                    
                    text = f"""📋 *Информация о кеше*

🕐 Возраст: {age_hours:.1f} часов
📊 Статус: {status}
📁 Категорий: {cache_info['total_categories']}
🏷️ Типы: {', '.join(cache_info['category_types'])}
📅 Создан: {cache_info['timestamp'][:16]}"""
            else:
                text = "❌ *Кеш не найден*\n\nКеш категорий не существует или поврежден."
            
            self.bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_management")
                )
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_clear_cache(self, call: CallbackQuery):
        """Обработчик очистки кеша"""
        try:
            success = self.sheets_client.cache_manager.clear_cache()
            
            if success:
                text = "✅ *Кеш очищен*\n\nКеш категорий успешно удален."
            else:
                text = "❌ *Ошибка очистки*\n\nНе удалось очистить кеш."
            
            self.bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_management")
                )
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_system_status(self, call: CallbackQuery):
        """Обработчик статуса системы"""
        try:
            # Простая проверка статуса
            cache_info = self.sheets_client.get_cache_info()
            
            # Проверяем подключение к Google Sheets
            try:
                test_data = self.sheets_client.get_all_data('Сводка')
                sheets_status = "🟢 Подключен"
            except Exception:
                sheets_status = "🔴 Ошибка подключения"
            
            # Статус кеша
            if cache_info['exists'] and not cache_info.get('is_expired', True):
                cache_status = "🟢 Действительный"
            elif cache_info['exists']:
                cache_status = "🟡 Истек"
            else:
                cache_status = "🔴 Отсутствует"
            
            text = f"""📊 *Статус системы*

🔗 Google Sheets: {sheets_status}
💾 Кеш категорий: {cache_status}
🤖 Бот: 🟢 Работает

📋 Информация:
• Пользователей в сессии: {len(self.user_data)}
• Версия: 1.0"""
            
            self.bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_management")
                )
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_back_to_management(self, call: CallbackQuery):
        """Обработчик возврата к управлению"""
        try:
            self.bot.edit_message_text(
                "⚙️ *Управление ботом*\n\nВыберите действие:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_management_keyboard()
            )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_delete_transaction_selection(self, call: CallbackQuery):
        """Обработчик выбора транзакции для удаления"""
        try:
            # Парсим callback_data: delete_trans_10_расходы
            parts = call.data.split('_')
            if len(parts) < 4:
                self.bot.answer_callback_query(call.id, "❌ Ошибка данных")
                return
            
            row_index = int(parts[2])
            transaction_type = parts[3]
            
            # Получаем данные о транзакции
            df = self.sheets_client.get_transactions_df("все")
            transaction_data = df[df['Строка'] == row_index]
            
            if transaction_data.empty:
                self.bot.answer_callback_query(call.id, "❌ Транзакция не найдена")
                return
            
            row = transaction_data.iloc[0]
            
            # Показываем подтверждение удаления
            confirmation_text = f"""
🗑️ *Подтверждение удаления*

Вы уверены, что хотите удалить эту транзакцию?

{'💸' if row['Тип'] == 'Расходы' else '💰'} **{row['Тип']}**
📅 Дата: {row['Дата']}
💰 Сумма: {row['Сумма']}
🏷️ Категория: {row['Категория']}
📝 Описание: {row['Описание']}
            """
            
            self.bot.edit_message_text(
                confirmation_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_delete_confirmation_keyboard(row_index, transaction_type)
            )
            
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    
    def handle_confirm_delete_transaction(self, call: CallbackQuery):
        """Обработчик подтверждения удаления транзакции"""
        try:
            # Парсим callback_data: confirm_delete_10_расходы
            parts = call.data.split('_')
            if len(parts) < 4:
                self.bot.answer_callback_query(call.id, "❌ Ошибка данных")
                return
            
            row_index = int(parts[2])
            transaction_type = parts[3]
            
            # Удаляем транзакцию
            self.sheets_client.delete_transaction(row_index, transaction_type)
            
            # Показываем успех
            self.bot.edit_message_text(
                "✅ *Транзакция удалена*\n\nТранзакция успешно удалена из Google Sheets.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
            # Показываем главное меню
            self.bot.send_message(
                call.message.chat.id,
                "🏦 *Главное меню*\n\nВыберите действие:",
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard()
            )
            
            self.bot.answer_callback_query(call.id, "✅ Транзакция удалена")
        except Exception as e:
            self.bot.edit_message_text(
                f"❌ *Ошибка удаления*\n\n{str(e)}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
                )
            )
            self.bot.answer_callback_query(call.id, "❌ Произошла ошибка")
    

    

    

    
    def run(self):
        """Запуск бота"""
        try:
            self.bot.infinity_polling(none_stop=True)
        except Exception as e:
            raise 