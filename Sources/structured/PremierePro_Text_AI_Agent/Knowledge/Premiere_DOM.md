# Premiere DOM

> **Tags:** #premiere-pro #extendscript #uxp #dom #hierarchy #object-model
> **Status:** Active
> **Version:** 1.0.0
> **Last Updated:** 2026-06-27

---

## 1. Суть и Назначение (Overview)
**Premiere Document Object Model (DOM)** — это иерархическая структура объектов, представляющая открытый проект и все его элементы внутри Premiere Pro. Скрипты ExtendScript и UXP взаимодействуют с этой моделью для управления файлами, таймлайнами, нарезкой клипов, наложением эффектов и рендерингом.

---

## 2. Архитектура и Взаимодействие (Architecture & Relations)

Иерархия объектов Premiere Pro DOM выглядит следующим образом:

```
 app (Application)
  └── project (Project)
       ├── rootItem (ProjectItem - Root Bin)
       │    └── children (Collection of ProjectItems: Bins, Clips, Subclips)
       └── sequences (SequenceCollection)
            └── Sequence (Timeline)
                 ├── markers (MarkerCollection)
                 ├── videoTracks (TrackCollection)
                 │    └── Track
                 │         └── clips (TrackItemCollection - Clips on Timeline)
                 │              └── components (ComponentCollection - Effects)
                 │                   └── properties (ComponentParamCollection)
                 └── audioTracks (TrackCollection)
                      └── Track
                           └── clips (TrackItemCollection - Audio Clips)
```

---

## 3. Справочник API (API Reference)

### 3.1. Корневые объекты

#### `Application` (глобальный объект `app`)
Входная точка.
*   `app.project`: Возвращает текущий активный объект `Project`.
*   `app.isDocumentOpen()`: Проверка, открыт ли хоть один проект (`true`/`false`).
*   `app.enableQE()`: Включение QE DOM (Quality Engineering).

#### `Project` (`app.project`)
Представляет файл проекта `.prproj`.
*   `project.activeSequence`: Возвращает текущую активную `Sequence` (фокусированную на таймлайне).
*   `project.sequences`: Коллекция всех эпизодов в проекте.
*   `project.rootItem`: Корневая папка (Bin) в панели Project. Имеет тип `ProjectItem`.
*   `project.importFiles(filePaths, suppressUI, targetBin, importAsNumberedStills)`: Импортирует файлы в указанный Bin.
*   `project.save()`: Сохраняет проект.
*   `project.close()`: Закрывает проект.

### 3.2. Элементы проекта (Project Items)

#### `ProjectItem`
Любой ассет в панели Project (папка, видеоклип, аудиоклип, эпизод, титр).
*   `projectItem.name`: Имя элемента.
*   `projectItem.type`: Тип элемента (целое число):
    *   `1`: Bin (папка).
    *   `2`: Clip (медиа-ресурс).
    *   `3`: Sequence (эпизод).
*   `projectItem.children`: Коллекция дочерних элементов (доступно только для `type == 1` / Bins).
*   `projectItem.treePath`: Полный путь элемента в структуре проекта (например, `Root\\Footage\\B-Roll`).
*   `projectItem.getMediaFilePath()`: Возвращает путь к исходному файлу на диске.

### 3.3. Эпизоды и Таймлайн (Sequences & Tracks)

#### `Sequence`
Представляет таймлайн.
*   `sequence.name`: Название таймлайна.
*   `sequence.id`: Уникальный ID.
*   `sequence.videoTracks`: Коллекция видеодорожек.
*   `sequence.audioTracks`: Коллекция аудиодорожек.
*   `sequence.markers`: Коллекция маркеров таймлайна.
*   `sequence.getInPoint()` / `sequence.getOutPoint()`: Получить границы рендеринга таймлайна в секундах.
*   `sequence.setInPoint(seconds)` / `sequence.setOutPoint(seconds)`: Установить границы.

#### `Track`
Отдельная дорожка (Video или Audio) на таймлайне.
*   `track.name`: Имя дорожки (например, `V1`, `Audio 1`).
*   `track.mediaType`: Тип медиа (`"video"` или `"audio"`).
*   `track.clips`: Коллекция элементов `TrackItem`, лежащих на этой дорожке.
*   `track.isMuted()` / `track.setMuted(state)`: Управление звуком дорожки (только для аудио).
*   `track.isLocked()` / `track.setLocked(state)`: Блокировка дорожки.

#### `TrackItem` (Clip на таймлайне)
Сегмент видео или аудио на дорожке.
*   `trackItem.name`: Название клипа.
*   `trackItem.start`: Начало клипа на таймлайне (объект `Time`).
*   `trackItem.end`: Конец клипа на таймлайне (объект `Time`).
*   `trackItem.inPoint`: Точка входа в исходное медиа (объект `Time`).
*   `trackItem.outPoint`: Точка выхода в исходном медиа (объект `Time`).
*   `trackItem.projectItem`: Ссылка на исходный `ProjectItem` в панели проекта.
*   `trackItem.components`: Коллекция эффектов, примененных к клипу.

---

## 4. Ограничения и Известные Проблемы (Limitations & Bugs)

1.  **Инпуты времени (Time Object)**: Время в Premiere измеряется в "тиках" (`Ticks`). Вычисления в секундах (дробные числа float) могут приводить к ошибкам округления на стыках клипов. Для точных операций всегда конвертируйте в Ticks.
2.  **Свойство `activeSequence`**: Может возвращать `null`, если панель Timeline не активна (например, фокус на панели Effect Controls).
3.  **Невозможность перемещения клипов через стандартный DOM**: В официальном DOM нет методов для свободного перемещения `TrackItem` с дорожки на дорожку или изменения его позиции `start`. Изменение `trackItem.start` может приводить к ошибкам и наложению клипов без предупреждения.
4.  **Различие между инстансом на таймлайне и исходником**:
    *   `TrackItem` — это экземпляр клипа на таймлайне.
    *   `ProjectItem` — это исходный файл в бине проекта.
    Изменение свойств `ProjectItem` (например, метаданных) не всегда синхронно обновляет `TrackItem` на таймлайне.

---

## 5. Reverse Engineering и Недокументированные Возможности

### Взаимосвязь с QE DOM
Официальный DOM Premiere Pro не позволяет выполнять монтажные операции (резать клип, делать insert/overwrite в произвольную точку времени с точностью до кадра). Для этого используется QE API:
*   `qe.project.getActiveSequence()`: Возвращает QE-эпизод.
*   `qe.sequence.getVideoTrackAt(index)`: Возвращает дорожку QE.
*   `qe.track.insertClip(projectItem, time)`: Вставка клипа по времени.

---

## 6. Распространенные Ошибки и Антипаттерны (Anti-patterns)

*   **Антипаттерн: Прямое сравнение строк при поиске дорожек**
    Не полагайтесь на имя дорожки (`track.name == "V1"`), так как пользователь может переименовать дорожку.
    *Решение:* Перебирайте дорожки по индексу и проверяйте `mediaType`.

*   **Антипаттерн: Рекурсивный обход Bins без проверки на циклы**
    Если папка внутри проекта содержит ссылки на саму себя (крайне редкий баг, но возможен при импорте XML), скрипт зависнет в бесконечном цикле.
    *Решение:* Всегда ведите список посещенных `id` или `treePath`.

---

## 7. Production-Ready Примеры Кода

### 1. Рекурсивный поиск файла в папках проекта (Bins)
```javascript
(function() {
    // Функция рекурсивного поиска
    function findItemByName(folderItem, itemName) {
        var foundItem = null;
        var children = folderItem.children;
        
        for (var i = 0; i < children.numItems; i++) {
            var currentItem = children[i];
            
            if (currentItem.name === itemName) {
                return currentItem;
            }
            
            // Если это папка (Bin), ищем внутри нее
            if (currentItem.type === 1) { // 1 = Bin
                foundItem = findItemByName(currentItem, itemName);
                if (foundItem !== null) {
                    return foundItem;
                }
            }
        }
        return null;
    }

    var project = app.project;
    if (project) {
        var fileToFind = "interview_audio.wav";
        var result = findItemByName(project.rootItem, fileToFind);
        if (result) {
            $.writeln("Найден файл: " + result.name + " (" + result.treePath + ")");
        } else {
            $.writeln("Файл не найден в проекте.");
        }
    }
})();
```

### 2. Получение списка всех клипов на активном таймлайне (V1 дорожка)
```javascript
(function() {
    var project = app.project;
    if (!project) return;
    
    var activeSeq = project.activeSequence;
    if (!activeSeq) {
        $.writeln("Нет активного эпизода.");
        return;
    }
    
    var vTracks = activeSeq.videoTracks;
    if (vTracks.numTracks === 0) {
        $.writeln("Нет видеодорожек на таймлайне.");
        return;
    }
    
    var firstTrack = vTracks[0]; // Первая видеодорожка (V1)
    var clips = firstTrack.clips;
    
    $.writeln("Клипы на дорожке " + firstTrack.name + ":");
    for (var i = 0; i < clips.numItems; i++) {
        var clip = clips[i];
        $.writeln(" - [" + i + "] " + clip.name + " (Начало: " + clip.start.seconds + " сек, Длительность: " + (clip.end.seconds - clip.start.seconds) + " сек)");
    }
})();
```

---

## 8. Практические Рекомендации (Best Practices)

1.  **Кэшируйте вызовы `children.numItems`**: Обращение к DOM Premiere работает медленно. Вместо `for (var i = 0; i < folder.children.numItems; i++)` сохраняйте количество элементов в переменную: `var len = folder.children.numItems; for (var i = 0; i < len; i++)`.
2.  **Защита от `null`**: Перед обращением к любому дочернему объекту (например, `trackItem.projectItem`) делайте проверку на `null`/`undefined`. Некоторые системные дорожки или генераторы (например, Adjustment Layers) могут не иметь связанного `ProjectItem`.

---

## 9. Источники (Sources & References)
*   [Adobe Premiere Pro Scripting API Reference (Official)](https://ppro-scripting.docsforadobe.dev/)
*   [Adobe CEP Samples on GitHub](https://github.com/Adobe-CEP/Samples/tree/master/PProPanel)
