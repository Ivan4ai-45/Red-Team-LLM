#!/bin/bash
# run_promptfoo.sh
# Использование: ./run_promptfoo.sh <путь_к_конфигу.yaml>

if [ -z "$1" ]; then
    echo "❌ Укажите путь к конфигурационному файлу"
    echo "Пример: ./run_promptfoo.sh promptfooconfig.yaml"
    exit 1
fi

CONFIG_FILE="$1"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Файл конфигурации не найден: $CONFIG_FILE"
    exit 1
fi

echo "🚀 Запуск Promptfoo Red Team с конфигом: $CONFIG_FILE"
npx promptfoo@latest redteam run --config "$CONFIG_FILE"

# Генерация HTML-отчёта (опционально)
echo "📊 Генерация HTML-отчёта..."
npx promptfoo@latest redteam report --config "$CONFIG_FILE"

echo "✅ Готово. Отчёт сохранён в текущей директории."