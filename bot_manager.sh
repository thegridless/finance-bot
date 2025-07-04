#!/bin/bash

# Скрипт для управления Finance Bot через Screen
# Использование: ./bot_manager.sh [start|stop|status|connect|logs]

# Настройки
BOT_NAME="finance-bot"
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$BOT_DIR/venv"
PYTHON_SCRIPT="$BOT_DIR/main.py"
LOG_FILE="$BOT_DIR/logs/bot.log"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функции для вывода
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Проверка установки screen
check_screen() {
    if ! command -v screen &> /dev/null; then
        print_error "Screen не установлен!"
        echo "Установите screen командой:"
        echo "  macOS: brew install screen"
        echo "  Ubuntu: sudo apt install screen"
        exit 1
    fi
}

# Проверка зависимостей
check_dependencies() {
    if [[ ! -d "$VENV_PATH" ]]; then
        print_error "Виртуальное окружение не найдено: $VENV_PATH"
        exit 1
    fi
    
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        print_error "Скрипт бота не найден: $PYTHON_SCRIPT"
        exit 1
    fi
    
    if [[ ! -f "$BOT_DIR/.env" ]]; then
        print_warning ".env файл не найден в $BOT_DIR"
    fi
    
    # Создаем директорию для логов
    mkdir -p "$BOT_DIR/logs"
}

# Проверка статуса бота
check_bot_status() {
    if screen -ls | grep -q "$BOT_NAME"; then
        return 0  # Бот запущен
    else
        return 1  # Бот не запущен
    fi
}

# Запуск бота
start_bot() {
    print_info "Запуск Finance Bot..."
    
    if check_bot_status; then
        print_warning "Бот уже запущен!"
        return 0
    fi
    
    # Создаем screen сессию и запускаем бота
    screen -dmS "$BOT_NAME" bash -c "
        cd '$BOT_DIR' && 
        source '$VENV_PATH/bin/activate' && 
        python '$PYTHON_SCRIPT' 2>&1 | tee -a '$LOG_FILE'
    "
    
    sleep 2
    
    if check_bot_status; then
        print_success "Бот успешно запущен!"
        print_info "Для подключения к сессии: ./bot_manager.sh connect"
        print_info "Для просмотра логов: ./bot_manager.sh logs"
    else
        print_error "Не удалось запустить бота"
        exit 1
    fi
}

# Остановка бота
stop_bot() {
    print_info "Остановка Finance Bot..."
    
    if ! check_bot_status; then
        print_warning "Бот не запущен"
        return 0
    fi
    
    # Завершаем screen сессию
    screen -S "$BOT_NAME" -X quit
    
    sleep 1
    
    if ! check_bot_status; then
        print_success "Бот успешно остановлен"
    else
        print_error "Не удалось остановить бота"
        exit 1
    fi
}

# Статус бота
show_status() {
    echo "=== Статус Finance Bot ==="
    
    if check_bot_status; then
        print_success "Бот запущен"
        echo ""
        echo "Активные screen сессии:"
        screen -ls | grep "$BOT_NAME"
    else
        print_warning "Бот не запущен"
    fi
    
    echo ""
    echo "Все screen сессии:"
    screen -ls
}

# Подключение к сессии
connect_to_bot() {
    if ! check_bot_status; then
        print_error "Бот не запущен"
        exit 1
    fi
    
    print_info "Подключение к сессии бота..."
    print_info "Для отключения нажмите Ctrl+A, затем D"
    sleep 2
    
    # Подключаемся к сессии
    screen -r "$BOT_NAME"
}

# Просмотр логов
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        print_info "Показываю логи (Ctrl+C для выхода):"
        tail -f "$LOG_FILE"
    else
        print_warning "Файл логов не найден: $LOG_FILE"
    fi
}

# Перезапуск бота
restart_bot() {
    print_info "Перезапуск Finance Bot..."
    stop_bot
    sleep 2
    start_bot
}

# Справка
show_help() {
    echo "🤖 Finance Bot Manager"
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Команды:"
    echo "  start     - Запустить бота"
    echo "  stop      - Остановить бота"
    echo "  restart   - Перезапустить бота"
    echo "  status    - Показать статус"
    echo "  connect   - Подключиться к сессии"
    echo "  logs      - Показать логи"
    echo "  help      - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 start    # Запустить бота"
    echo "  $0 status   # Проверить статус"
    echo "  $0 connect  # Подключиться к сессии"
}

# Основная функция
main() {
    check_screen
    check_dependencies
    
    case "${1:-help}" in
        start)
            start_bot
            ;;
        stop)
            stop_bot
            ;;
        restart)
            restart_bot
            ;;
        status)
            show_status
            ;;
        connect)
            connect_to_bot
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Неизвестная команда: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Запуск
main "$@" 