# VFX List Export Tool для Adobe Premiere Pro 2026

Профессиональный инструмент для управления маркерами, субтитрами и MOGRT текстом в Premiere Pro.

## Исправления

### Fix #1: Авто-определение смещённых маркеров ✅
**Проблема**: Маркеры не автоматически определялись как смещённые и не фильтровались по цвету.

**Решение**:
- `Block1_VFXList.analyze_markers()` классифицирует маркеры
- Авто-определение по паттернам: CG, VFX, SFX, числовые суффиксы
- `filter_by_color()` фильтрует по цвету таймлайна
- `get_color_groups()` группирует по цветам

### Fix #2: TC Range (IN-OUT) ✅
**Проблема**: Диапазон IN-OUT маркеров игнорировался при переименовании.

**Решение**:
- `TimelineHelper` конвертирует frame ↔ seconds
- Фильтрация по диапазону через `limit_to_range=True`
- Параметры `in_frame` и `out_frame`

### Fix #3: Переименование субтитров в пакетном режиме ✅
**Проблема**: Функция переименования субтитров не работала.

**Решение**:
- `Block4_RenameRenumber.prepare_caption_renaming()` подготавливает обновления
- Генерирует ExtendScript для выполнения в Premiere
- Поддержка шаблонов: `"CAP_{shot}"` → `"CAP_0001"`
- Каждый субтитр открывается и обновляется последовательно

**Использование**:
```python
tool = VFXListExportTool()
captions = [CaptionInfo(...), ...]
mapping, script = tool.process_captions_batch(
    captions, 
    "EPISODE_02_CAP_{shot}",
    limit_to_range=True,
    in_frame=in_frame,
    out_frame=out_frame
)
tool.execute_extendscript(script)
```

### Fix #4: Переименование MOGRT текста в пакетном режиме ✅
**Проблема**: Текст в MOGRT/текстовых плашках не обновлялся.

**Решение**:
- `Block4_RenameRenumber.prepare_mogrt_renaming()` подготавливает обновления
- Работает с JSON blob метадеев MOGRT (Source Text)
- **Критично**: Обновляет `fontTextRunLength` согласно длине текста
- Генерирует ExtendScript для выполнения в Premiere

**Как работает**:
1. Каждый MOGRT имеет JSON blob с текстом:
   ```json
   {
     "textEditValue": "Old Text",
     "fontTextRunLength": [8],
     "fontEditValue": ["Arial"]
   }
   ```

2. ExtendScript обновляет blob:
   ```javascript
   blob.textEditValue = "New Text";
   blob.fontTextRunLength = [8];  // MUST equal new text length
   param.setValue(JSON.stringify(blob), true);
   ```

3. Обновления применяются в Premiere Pro

**Использование**:
```python
mogrt_clips = [MOGRTInfo(...), ...]
updates, script = tool.process_mogrt_batch(
    mogrt_clips,
    "PLATE_{shot}",
    limit_to_range=True
)
tool.execute_extendscript(script)
```

### Fix #5: Система кастомных шаблонов ✅
**Решение**:
- `PresetsManager` для сохранения/загрузки конфигураций
- Встроенные preset: "Default", "Multicam"
- Экспорт/импорт для передачи между пользователями
- Сохраняются в `~/.vfx_export_tool_premiere/presets.json`

**Использование**:
```python
pm = tool.presets

# Загрузить preset
settings = pm.load_preset("Default")

# Сохранить свой preset
my_config = {
    "project_prefix": "OTV",
    "episode": "02",
    "caption_pattern": "OTV_EP02_CAP_{shot}",
    "mogrt_pattern": "OTV_EP02_PLATE_{shot}"
}
pm.save_preset("OTV_Episode02", my_config)

# Экспортировать для передачи
pm.export_preset("OTV_Episode02", "/Desktop/ep02.json")

# Импортировать полученный preset
pm.import_preset("Imported", "/Downloads/ep02.json")
```

## Архитектура

### Python Components
- **TimelineHelper** - конвертация frame/seconds
- **Block1_VFXList** - анализ маркеров
- **Block4_RenameRenumber** - подготовка обновлений
- **ExtendScriptBridge** - генерация ExtendScript кода
- **PresetsManager** - система шаблонов
- **VFXListExportTool** - оркестратор

### ExtendScript Integration
Пакетные операции выполняются через ExtendScript, который:
1. Работает внутри Premiere Pro процесса
2. Имеет прямой доступ к DOM
3. Может читать/писать MOGRT JSON blobs
4. Обновляет clip names и свойства
5. Гарантирует консистентность данных

## Рабочий процесс

### 1. Анализ маркеров (Block 1)
```python
block1 = Block1_VFXList([marker1, marker2, ...])
markers = block1.analyze_markers()
displaced = block1.displaced_markers  # Только CG/VFX/SFX
colors = block1.get_color_groups()    # Группировка по цвету
```

### 2. Переименование субтитров (Block 4 Part A)
```python
# Подготовка
captions = [CaptionInfo(...), ...]
mapping, script = tool.process_captions_batch(
    captions,
    "OTV_EP02_CAP_{shot}",  # Шаблон
    limit_to_range=True,     # Только в диапазоне TC
    in_frame=in_frame,
    out_frame=out_frame
)

# Результат mapping: {"Old Caption 1" → "OTV_EP02_CAP_0001", ...}

# Выполнение (внутри Premiere)
tool.execute_extendscript(script)
```

### 3. Переименование MOGRT (Block 4 Part B)
```python
# Подготовка
mogrt_list = [MOGRTInfo(...), ...]
updates, script = tool.process_mogrt_batch(
    mogrt_list,
    "PLATE_{shot}",        # Шаблон
    limit_to_range=True
)

# Результат updates: {
#   "1_1": {
#     "old_text": "Old Title",
#     "new_text": "PLATE_0001",
#     "json_blob": {"textEditValue": "PLATE_0001", "fontTextRunLength": [9], ...}
#   }
# }

# Выполнение
tool.execute_extendscript(script)
```

### 4. Управление шаблонами (Presets)
```python
# Сохранение текущих настроек
settings = {
    "caption_pattern": "EP{ep}_CAP_{shot}",
    "mogrt_pattern": "EP{ep}_PLATE_{shot}",
    "episode": "02"
}
tool.presets.save_preset("EP02_Config", settings)

# Загрузка при следующем запуске
loaded = tool.presets.load_preset("EP02_Config")

# Обмен с коллегами
tool.presets.export_preset("EP02_Config", "/shared/ep02.json")
```

## Генерируемый ExtendScript

### Для субтитров
```javascript
// Итерирует по видео-трекам, находит caption clips
// Обновляет их names согласно mapping
for (var t = 1; t <= seq.videoTracks.numTracks; t++) {
    var track = seq.videoTracks[t-1];
    for (var c = 1; c <= track.clips.numTracks; c++) {
        var clip = track.clips[c-1];
        if (clip && captionMap[clip.name]) {
            clip.name = captionMap[clip.name];  // Update
        }
    }
}
```

### Для MOGRT
```javascript
// updateMogrtText() - production-safe pattern
// 1. Получает MOGRT component
// 2. Парсит Source Text JSON blob
// 3. Обновляет textEditValue и fontTextRunLength
// 4. Применяет через param.setValue()
// КРИТИЧНО: fontTextRunLength MUST = textEditValue.length
var blob = JSON.parse(param.getValue());
blob.textEditValue = newText;
blob.fontTextRunLength = [newText.length];  // <-- MANDATORY
param.setValue(JSON.stringify(blob), true);
```

## Требования

- Adobe Premiere Pro 2026 (или 2024+)
- Python 3.6+
- ExtendScript поддержка в Premiere (активна по умолчанию)

## Файлы

- `vfx_list_export_tool_premiere.py` - основной инструмент (Python)
- `VFX_TOOL_PREMIERE_GUIDE.md` - документация (этот файл)

## Примеры шаблонов

### Для субтитров
- `"CAP_{shot}"` → CAP_0001, CAP_0002
- `"EP{ep}_CAP_{shot}"` → EP02_CAP_0001, EP02_CAP_0002
- `"SUB_{shot}_EN"` → SUB_0001_EN, SUB_0002_EN

### Для MOGRT
- `"PLATE_{shot}"` → PLATE_0001, PLATE_0002
- `"LOWER_THIRD_{shot}"` → LOWER_THIRD_0001
- `"EP{ep}_SHOT_{shot}"` → EP02_SHOT_0001

## Troubleshooting

**Q: MOGRT текст не обновляется**
A: Проверьте что MOGRT создан в After Effects с "Allow font/style editing" включён. Параметр должен быть доступен как "Source Text" или "Text".

**Q: fontTextRunLength критичен?**
A: ДА. Если не совпадает с длиной текста, текст не будет отображаться или стилизация развалится.

**Q: Как запустить ExtendScript в Premiere?**
A: Сценарий сохраняется в temp файл. Откройте его вручную через:
File → Scripts → Run Script (AdobeUME) → выберите файл
Или используйте PPRO Extensions если доступны.

**Q: Работает ли без диапазона TC?**
A: Да, оставьте `limit_to_range=False` или не передавайте `in_frame/out_frame`.

## Интеграция

Инструмент готов к:
1. Встраиванию в Premiere Panel (UXP)
2. Использованию как standalone Python скрипт
3. Интеграции с другими automation tools
