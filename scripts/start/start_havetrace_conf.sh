#!/bin/bash
# run_hivetrace.sh
# Использование: ./run_hivetrace.sh <путь_к_конфигу.yaml>

if [ -z "$1" ]; then
    echo "❌ Укажите путь к конфигурационному файлу"
    echo "Пример: ./run_hivetrace.sh hivetrace_config.yaml"
    exit 1
fi

CONFIG_FILE="$1"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Файл конфигурации не найден: $CONFIG_FILE"
    exit 1
fi

echo "🚀 Запуск HiveTrace Red с конфигом: $CONFIG_FILE"
hivetracered --config "$CONFIG_FILE"

echo "✅ Готово. Для генерации HTML-отчёта выполните:"
echo "hivetracered-report --data-file <папка_результатов>/evaluated_responses.parquet --output report.html"