#!/bin/bash
# install_promptfoo.sh
# Этот скрипт устанавливает Promptfoo глобально через npm.

set -e

echo "🚀 Начинаем установку Promptfoo..."

# 1. Проверка наличия Node.js (требуется версия 18+)
if ! command -v node &> /dev/null
then
    echo "❌ Node.js не найден. Пожалуйста, установите Node.js версии 18 или выше."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Версия Node.js ($(node -v)) устарела. Требуется версия 18 или выше."
    exit 1
fi
echo "✅ Node.js найден: $(node -v)"

# 2. Глобальная установка Promptfoo
npm install -g promptfoo@latest
echo "✅ Promptfoo успешно установлен глобально."

# 3. Финальное сообщение
echo "🎉 Установка завершена!"
echo "👉 Для проверки установки выполните: promptfoo --version"
echo "👉 Чтобы начать работу в текущей директории, выполните: npx promptfoo init"