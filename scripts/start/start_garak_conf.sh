#!/bin/bash
# run_garak.sh
# Использование: ./run_garak.sh <путь_к_конфигу.yaml>

if [ -z "$1" ]; then
    echo "❌ Укажите путь к конфигурационному файлу"
    echo "Пример: ./run_garak.sh garak_config.yaml"
    exit 1
fi

CONFIG_FILE="$1"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Файл конфигурации не найден: $CONFIG_FILE"
    exit 1
fi

echo "🚀 Запуск Garak с конфигом: $CONFIG_FILE"
garak --config "$CONFIG_FILE"

echo "✅ Сканирование Garak завершено."