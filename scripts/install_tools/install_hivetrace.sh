#!/bin/bash
# install_hivetrace.sh
# Этот скрипт устанавливает HiveTrace Red в виртуальном окружении Python.

set -e  # Остановить скрипт при любой ошибке

echo "🚀 Начинаем установку HiveTrace Red..."

# 1. Создание и активация виртуального окружения
python3 -m venv hivetrace_env
echo "✅ Виртуальное окружение 'hivetrace_env' создано."

# 2. Активация окружения
source hivetrace_env/bin/activate
echo "✅ Виртуальное окружение активировано."

# 3. Установка HiveTrace Red через pip
pip install --upgrade pip
pip install hivetracered
echo "✅ HiveTrace Red успешно установлен."

# 4. Установка веб-инструментов (опционально)
pip install 'hivetracered[web]'
echo "✅ Веб-инструменты установлены."

# 5. Финальное сообщение
echo "🎉 Установка завершена!"
echo "👉 Для активации окружения в будущем используйте: source hivetrace_env/bin/activate"
echo "👉 После активации будут доступны команды: hivetracered, hivetracered-report, hivetracered-recorder"
echo "👉 Документация: https://hivetrace.github.io/HiveTraceRed/"