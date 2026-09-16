#!/bin/bash

# Установщик скрипта DaVinci Resolve для пакетного экспорта по маркерам

SCRIPT_NAME="export_by_markers.py"
SOURCE_SCRIPT="/Users/konstantinguryanov/Documents/-open-premiere-specification/${SCRIPT_NAME}"
DAVINCI_SCRIPTS_DIR="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"

echo "🎬 Установка скрипта DaVinci Resolve для экспорта по маркерам..."

# Проверка исходного файла
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "❌ Ошибка: исходный файл не найден"
    echo "   Ожидаемый путь: $SOURCE_SCRIPT"
    exit 1
fi

# Создание директории если её нет
if [ ! -d "$DAVINCI_SCRIPTS_DIR" ]; then
    echo "📁 Создание директории для скриптов..."
    mkdir -p "$DAVINCI_SCRIPTS_DIR" || {
        echo "❌ Ошибка: нет прав для создания директории"
        exit 1
    }
fi

# Копирование скрипта
echo "📋 Копирование скрипта..."
cp "$SOURCE_SCRIPT" "$DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME" || {
    echo "❌ Ошибка при копировании"
    exit 1
}

# Установка прав доступа
chmod 755 "$DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME"

# Проверка установки
if [ -f "$DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME" ]; then
    echo "✅ Скрипт успешно установлен!"
    echo "   Путь: $DAVINCI_SCRIPTS_DIR/$SCRIPT_NAME"
    echo ""
    echo "📖 Как использовать:"
    echo "   1. Откройте DaVinci Resolve"
    echo "   2. Верхнее меню → Fairlight → Workspace → Scripts"
    echo "   3. Выберите 'export_by_markers'"
    echo ""
    echo "⚙️  Перед запуском:"
    echo "   • Убедитесь, что у вас есть активный таймлайн"
    echo "   • Добавьте маркеры на клипы"
    echo "   • Скрипт создаст папку ~/Desktop/Export с видеофайлами"
else
    echo "❌ Ошибка: скрипт не появился в целевой директории"
    exit 1
fi
