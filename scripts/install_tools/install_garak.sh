+#!/bin/bash
# install_garak.sh
# Этот скрипт устанавливает Garak в новом виртуальном окружении Python.

set -e  # Остановить скрипт при любой ошибке

echo "🚀 Начинаем установку Garak..."

# 1. Создание и активация виртуального окружения
python3 -m venv garak_env
echo "✅ Виртуальное окружение создано."

# 2. Активация окружения
source garak_env/bin/activate
echo "✅ Виртуальное окружение активировано."

# 3. Установка Garak из PyPI
pip install --upgrade pip
pip install garak
echo "✅ Garak успешно установлен."

# 4. Финальное сообщение
echo "🎉 Установка завершена!"
echo "👉 Для активации окружения в будущем используйте: source garak_env/bin/activate"
echo "👉 Для проверки установки выполните: garak --list_probes"