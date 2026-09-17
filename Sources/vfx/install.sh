#!/bin/bash

# Простой установщик DaVinci Resolve Export by Markers Script
# Использование: sudo ./install.sh

set -e

SCRIPT_NAME="export_by_markers.lua"
DAVINCI_SCRIPTS_DIR="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"

echo "🎬 Установка DaVinci Resolve Export by Markers Script"
echo ""

# Проверка прав администратора
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Требуются права администратора"
    echo "   Используй: sudo ./install.sh"
    exit 1
fi

# Поиск исходного скрипта
if [ -f "./$SCRIPT_NAME" ]; then
    SOURCE_SCRIPT="./$SCRIPT_NAME"
elif [ -f "$SCRIPT_NAME" ]; then
    SOURCE_SCRIPT="$SCRIPT_NAME"
else
    echo "❌ Ошибка: $SCRIPT_NAME не найден в текущей директории"
    exit 1
fi

# Создание директории если её нет
if [ ! -d "$DAVINCI_SCRIPTS_DIR" ]; then
    echo "📁 Создание директории скриптов DaVinci..."
    mkdir -p "$DAVINCI_SCRIPTS_DIR"
fi

# Копирование скрипта
echo "📋 Копирование скрипта..."
cp "$SOURCE_SCRIPT" "$DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME"

# Установка прав доступа
chmod 755 "$DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME"

# Проверка
if [ -f "$DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME" ]; then
    echo ""
    echo "✅ Успешно установлено!"
    echo ""
    echo "📍 Путь установки:"
    echo "   $DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME"
    echo ""
    echo "📖 Инструкция:"
    echo "   1. Перезагрузи DaVinci Resolve"
    echo "   2. Fairlight → Workspace → Scripts → Utility → export_by_markers"
    echo "   3. Добавь маркеры на таймлайн"
    echo "   4. Запусти скрипт"
    echo ""
else
    echo "❌ Ошибка установки"
    exit 1
fi
