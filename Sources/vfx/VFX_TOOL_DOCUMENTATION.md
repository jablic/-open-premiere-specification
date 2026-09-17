# VFX List Export Tool - Полная документация

## Обзор

Профессиональный инструмент для управления маркерами, субтитрами и текстовыми плашками в DaVinci Resolve. Включает автоматическое определение смещённых маркеров, переименование по шаблонам и систему сохранения настроек.

## Архитектура

### Основные компоненты

#### Block 1: VFX List
- **Назначение**: Анализ маркеров таймлайна и их классификация
- **Функции**:
  - Автоматическое определение смещённых маркеров (CG, VFX, SFX)
  - Фильтрация по цвету
  - Группировка маркеров по типам
  - Игнорирование IN/OUT маркеров

**Исправления**:
- ✅ Fix #1: Автоматическое определение смещённых маркеров с фильтрацией по цвету

#### Block 2: Video References
- Управление видео-референсами
- Сохранение и загрузка ссылок на видео

#### Block 3: Convert
- Преобразование между форматами
- Конвертация таймкодов
- Преобразование метаданных

#### Block 4: Rename & Renumber
- **Основные функции**:
  1. Переименование маркеров по шаблону
  2. Переименование субтитров
  3. Переименование текстовых плашек

**Исправления**:
- ✅ Fix #2: Правильное определение TC диапазона (IN-OUT) из маркеров таймлайна
- ✅ Fix #3: Реализована функция переименования субтитров с поддержкой шаблонов
- ✅ Fix #4: Реализована функция переименования текстовых плашек (mogrt)

#### Presets Manager (новое)
- **Назначение**: Сохранение и загрузка пользовательских шаблонов настроек
- **Функции**:
  - Сохранение текущих параметров как preset
  - Загрузка сохранённых конфигураций
  - Экспорт/импорт presets
  - Встроенные preset шаблоны (Default, Multicam)

**Исправление**:
- ✅ Fix #5: Полная система кастомных пользовательских шаблонов

## Классы и их назначение

### TimelineHelper
Вспомогательный класс для работы с таймлайном:
- Преобразование frame ↔ timecode
- Определение IN-OUT маркеров
- Доступ к информации о треках

### Block1_VFXList
Анализ и фильтрация маркеров:
```python
vfx_list = Block1_VFXList(timeline_helper)
markers = vfx_list.analyze_markers()
displaced = vfx_list.displaced_markers
color_groups = vfx_list.get_color_groups()
```

### Block4_RenameRenumber
Переименование маркеров, субтитров и плашек:
```python
# Переименование маркеров в диапазоне TC
markers = block4.get_markers_in_range(limit_to_range=True)
results = block4.rename_markers(markers, "OTV_EP{ep}_CG{shot}")

# Переименование субтитров
caption_results = block4.rename_captions("CAPTION_{shot}", limit_to_range=True)

# Переименование текстовых плашек
plate_results = block4.rename_text_plates("PLATE_{shot}", limit_to_range=True)
```

### PresetsManager
Управление пользовательскими настройками:
```python
presets = PresetsManager()

# Сохранение preset
settings = {"project_prefix": "OTV", "episode": "02", ...}
presets.save_preset("MyPreset", settings)

# Загрузка preset
loaded = presets.load_preset("MyPreset")

# Экспорт/импорт
presets.export_preset("MyPreset", "/path/to/preset.json")
presets.import_preset("Imported", "/path/to/preset.json")
```

## Исправления ошибок

### Bug #1: Auto-detection of Displaced Markers (FIXED ✅)

**Проблема**: VFX List не автоматически определял смещённые маркеры и не фильтровался по цвету.

**Решение**:
- Реализована функция `_detect_marker_type()` для классификации маркеров
- Добавлена фильтрация по цвету: `filter_by_color(color)`
- Добавлена группировка по цветам: `get_color_groups()`
- Маркеры автоматически определяются как "displaced" если содержат CG/VFX/SFX/числовые суффиксы

### Bug #2: TC Range (IN-OUT) Not Working (FIXED ✅)

**Проблема**: При включении "Limit to TC range (IN-OUT)" скрипт игнорировал диапазон и переименовывал ВСЕ маркеры.

**Решение**:
- Реализована функция `get_in_out_markers()` которая ищет IN и OUT маркеры на таймлайне
- Добавлена правильная фильтрация маркеров по диапазону в `get_markers_in_range()`
- TC поля теперь автоматически заполняются из маркеров IN-OUT
- Все операции переименования поддерживают параметр `limit_to_range`

**Как работает**:
1. На таймлайне создаются маркеры "IN" и "OUT"
2. При включении опции "Limit to TC range" скрипт находит эти маркеры
3. Переименование применяется только к маркерам между IN и OUT

### Bug #3: Caption Renaming Not Working (FIXED ✅)

**Проблема**: Функция переименования субтитров не работала, не было способа переименовать каждый субтитр по маске.

**Решение**:
- Реализована функция `rename_captions()` в Block4
- Поддержка шаблонов: `"CAPTION_{shot}"` → `"CAPTION_0001"`, `"CAPTION_0002"` и т.д.
- Поддержка TC range filtering
- Каждый субтитр получает уникальный номер согласно счётчику

**Использование**:
```python
results = block4.rename_captions("OTV_EP02_CAP_{shot}", limit_to_range=True)
# Результат: OTV_EP02_CAP_0001, OTV_EP02_CAP_0002, ...
```

### Bug #4: Text Plate Renaming Not Working (FIXED ✅)

**Проблема**: Функция переименования текстовых плашек (mogrt) не работала.

**Решение**:
- Реализована функция `rename_text_plates()` в Block4
- Функция ищет все текстовые элементы и mogrt клипы на видео-треках
- Поддержка шаблонов и TC range filtering
- Каждой плашке назначается уникальный номер

**Использование**:
```python
results = block4.rename_text_plates("PLATE_{shot}", limit_to_range=True)
# Результат: PLATE_0001, PLATE_0002, ...
```

### Bug #5: Custom Preset Templates System (FIXED ✅)

**Проблема**: Не было способа сохранять и передавать кастомные настройки.

**Решение**:
- Полная система PresetsManager для работы с шаблонами
- Встроенные presets: "Default" и "Multicam"
- Функции сохранения, загрузки, экспорта и импорта
- Presets сохраняются в `~/.vfx_export_tool/presets.json`

**Использование**:
```python
pm = PresetsManager()

# Сохранение текущих настроек
settings = {
    "project_prefix": "OTV",
    "episode": "02",
    "sequence": "1",
    "shot_type": "CG",
    "padding": 4,
    "marker_color": "Blue"
}
pm.save_preset("OTV_Episode02", settings)

# Загрузка preset
loaded = pm.load_preset("OTV_Episode02")

# Экспорт для передачи другому пользователю
pm.export_preset("OTV_Episode02", "/Desktop/ep02_settings.json")

# Импорт полученных настроек
pm.import_preset("Imported_EP02", "/Desktop/ep02_settings.json")
```

## Использование

### Базовое использование

```python
from vfx_list_export_tool import VFXListExportTool

tool = VFXListExportTool()

# Анализ маркеров
analysis = tool.run_analysis()
print(f"Найдено маркеров: {analysis['total_markers']}")
print(f"Смещённых: {analysis['displaced_markers']}")

# Переименование маркеров в диапазоне TC
results = tool.run_rename_markers(
    pattern="OTV_EP02_CG{shot}",
    start=1,
    step=1,
    limit_to_range=True
)

# Переименование субтитров
caption_results = tool.run_rename_captions(
    pattern="OTV_EP02_SUB_{shot}",
    limit_to_range=True
)

# Переименование текстовых плашек
plate_results = tool.run_rename_text_plates(
    pattern="OTV_EP02_PLATE_{shot}",
    limit_to_range=True
)
```

### Работа с Presets

```python
pm = tool.presets

# Список доступных presets
presets_list = pm.list_presets()
# ['Default', 'Multicam']

# Загрузка preset
default_settings = pm.load_preset("Default")

# Создание новой конфигурации и сохранение
my_settings = {
    "project_prefix": "TEST",
    "episode": "03",
    "sequence": "2",
    "shot_type": "VFX",
    "padding": 3,
    "start": 1,
    "step": 1,
    "marker_color": "Green"
}
pm.save_preset("TestProject", my_settings)

# Удаление preset
pm.delete_preset("TestProject")
```

## Примеры шаблонов (patterns)

### Для маркеров
- `"OTV_EP{ep}_CG{shot}"` → OTV_EP02_CG0001, OTV_EP02_CG0002
- `"{ep}_{shot}"` → 02_001, 02_002
- `"SHOT_{shot}_VFX"` → SHOT_0001_VFX, SHOT_0002_VFX

### Для субтитров
- `"SUB_{shot}"` → SUB_0001, SUB_0002
- `"CAP_{ep}_{shot}"` → CAP_02_0001, CAP_02_0002

### Для текстовых плашек
- `"PLATE_{shot}"` → PLATE_0001, PLATE_0002
- `"TEXT_{shot}"` → TEXT_0001, TEXT_0002

## Требования

- DaVinci Resolve 17.0+
- Python 3.6+
- Доступ к Resolve API

## Файлы

- `vfx_list_export_tool.py` - Основной инструмент (все классы и функции)
- `VFX_TOOL_DOCUMENTATION.md` - Документация (этот файл)

## Интеграция

Инструмент готов к использованию как:
1. Standalone Python скрипт в DaVinci Resolve
2. Импортируемый модуль для других скриптов
3. Основа для разработки UI панели
