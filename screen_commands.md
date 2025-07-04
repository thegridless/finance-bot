# 📺 Шпаргалка по Screen

## Основные команды

### Управление сессиями
```bash
screen -ls                    # Список всех сессий
screen -S <name>             # Создать сессию с именем
screen -r <name>             # Подключиться к сессии
screen -dr <name>            # Принудительно подключиться
screen -S <name> -X quit     # Завершить сессию
```

### Горячие клавиши (Ctrl+A, затем...)
```
d     # Отключиться от сессии
c     # Создать новое окно
n     # Следующее окно
p     # Предыдущее окно
"     # Список окон
A     # Переименовать окно
k     # Закрыть окно
S     # Разделить горизонтально
|     # Разделить вертикально
Tab   # Переключить между панелями
?     # Помощь
```

## Запуск Finance Bot

### Простой запуск
```bash
# Создать сессию
screen -S finance-bot

# Внутри сессии:
source finance_bot_env/bin/activate
python main.py

# Отключиться: Ctrl+A, затем D
```

### Проверка статуса
```bash
# Посмотреть сессии
screen -ls

# Подключиться обратно
screen -r finance-bot

# Завершить сессию
screen -S finance-bot -X quit
```

### Автоматический запуск
```bash
# Создать и сразу запустить команду
screen -dmS finance-bot bash -c 'cd /path/to/finance-bot && source finance_bot_env/bin/activate && python main.py'
```

## Полезные алиасы

Добавьте в ~/.bashrc или ~/.zshrc:
```bash
# Алиасы для управления finance-bot
alias bot-start='screen -dmS finance-bot bash -c "cd ~/finance-bot && source finance_bot_env/bin/activate && python main.py"'
alias bot-connect='screen -r finance-bot'
alias bot-stop='screen -S finance-bot -X quit'
alias bot-status='screen -ls | grep finance-bot'
```

## Логирование

Для сохранения логов:
```bash
# Включить логирование в сессии
Ctrl+A, затем H

# Или запустить с логированием
screen -L -S finance-bot
```

## Советы

1. **Всегда используйте именованные сессии** для легкого поиска
2. **Регулярно проверяйте список сессий** командой `screen -ls`
3. **Используйте алиасы** для упрощения команд
4. **Не забывайте отключаться** от сессий (Ctrl+A, D)
5. **Включите логирование** для отладки проблем 