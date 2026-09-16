#!/bin/bash

# Скрипт для создания PKG установщика DaVinci Resolve Script
# Использование: ./build_davinci_installer.sh

set -e

SCRIPT_NAME="export_by_markers.lua"
SOURCE_SCRIPT="./export_by_markers.lua"
OUTPUT_DIR="./davinci-script-installer"
PKG_NAME="DaVinci-Export-by-Markers.pkg"

echo "🔨 Сборка установщика DaVinci Resolve скрипта..."

# Проверка исходного файла
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "❌ Ошибка: $SOURCE_SCRIPT не найден"
    echo "   Скопируй export_by_markers.lua в текущую директорию"
    exit 1
fi

# Удаление старых файлов
rm -rf "$OUTPUT_DIR" "$PKG_NAME"

# Создание временной структуры для PKG
mkdir -p "$OUTPUT_DIR/root/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"

# Копирование скрипта
cp "$SOURCE_SCRIPT" "$OUTPUT_DIR/root/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/$SCRIPT_NAME"

# Установка прав доступа
chmod 755 "$OUTPUT_DIR/root/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/$SCRIPT_NAME"

# Создание скрипта post-install
mkdir -p "$OUTPUT_DIR/scripts"
cat > "$OUTPUT_DIR/scripts/postinstall" << 'POSTSCRIPT'
#!/bin/bash
# Post-install скрипт
SCRIPT_PATH="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/export_by_markers.lua"
chmod 755 "$SCRIPT_PATH"
echo "✅ Скрипт export_by_markers установлен успешно"
POSTSCRIPT

chmod 755 "$OUTPUT_DIR/scripts/postinstall"

# Сборка PKG
echo "📦 Сборка пакета..."
pkgbuild \
    --root "$OUTPUT_DIR/root" \
    --scripts "$OUTPUT_DIR/scripts" \
    --identifier com.custom.davinci.exportbymarkers \
    --version 1.0 \
    --install-location / \
    "$PKG_NAME"

# Очистка временных файлов
rm -rf "$OUTPUT_DIR"

echo "✅ Установщик создан: $PKG_NAME"
echo ""
echo "📋 Как использовать:"
echo "   1. Двойной клик на $PKG_NAME"
echo "   2. Следуй инструкциям установщика"
echo "   3. Перезагрузи DaVinci Resolve"
echo "   4. Скрипт появится в Fairlight → Workspace → Scripts → Utility"
echo ""
echo "🔗 Для распространения - можно поместить PKG в DMG образ:"
echo "   hdiutil create -volname 'DaVinci Export by Markers' -srcfolder . -ov -format UDZO davinci-export-installer.dmg"
