# ExtendScript

> **Tags:** #premiere-pro #extendscript #cep #jsx #reflection
> **Status:** Active
> **Version:** 1.0.0
> **Last Updated:** 2026-06-27

---

## 1. Суть и Назначение (Overview)
**ExtendScript** — это проприетарный диалект языка JavaScript (соответствующий стандарту ECMAScript 3), разработанный Adobe для автоматизации своих продуктов. В Premiere Pro ExtendScript выступает в роли "движка сценариев" (scripting engine), который имеет прямой доступ к внутренней объектной модели приложения (DOM) и может управлять проектами, эпизодами (sequences), клипами, маркерами, импортом и экспортом.

ExtendScript выполняется в собственном изолированном контексте (потоке JSX) и не имеет прямого доступа к сетевым запросам, DOM-дереву браузера или современным веб-технологиям.

---

## 2. Архитектура и Взаимодействие (Architecture & Relations)

В экосистеме Premiere Pro ExtendScript взаимодействует с другими компонентами по следующим схемам:

### CEP (Common Extensibility Platform)
CEP-панель (UI на HTML/CSS/JS) работает в процессе Chromium Embedded Framework (CEF). Скриптовый поток ExtendScript работает отдельно. Взаимодействие между ними асинхронное и строго строковое:
```
[ CEP UI (JS) ] -- CSInterface.evalScript("jsxFunction(arg)") --> [ ExtendScript Engine (JSX) ]
[ CEP UI (JS) ] <-- Callback c результатом (String) ------------- [ ExtendScript Engine (JSX) ]
```

### UXP (Unified Extensibility Platform)
В современных версиях Premiere Pro UXP может напрямую вызывать методы API Premiere Pro (через встроенные модули UXP) либо использовать мосты для выполнения традиционного ExtendScript.

---

## 3. Справочник API (API Reference)

### Глобальные объекты ExtendScript
*   `app`: Корневой объект Premiere Pro (входная точка автоматизации).
*   `$`: Вспомогательный объект отладки ExtendScript (содержит методы логирования, профилирования, управления движком).
*   `File`: Объект для работы с файлами на диске.
*   `Folder`: Объект для работы с директориями.
*   `Socket`: Предоставляет базовые возможности TCP-соединений.
*   `XML`: Встроенный E4X (ECMAScript for XML) парсер для работы с XML данными (очень быстрый и удобный).

### Основные методы отладки ($)
*   `$.write(msg1, msg2...)`: Вывод в консоль ExtendScript Toolkit / VS Code Debugger.
*   `$.writeln(msg1, msg2...)`: Вывод в консоль с новой строки.
*   `$.bp(cond)`: Точка останова (breakpoint) для отладки.
*   `$.sleep(milliseconds)`: Приостановка выполнения скрипта (блокирует интерфейс Premiere Pro!).
*   `$.about()`: Информация о движке ExtendScript.

---

## 4. Ограничения и Известные Проблемы (Limitations & Bugs)

1.  **Отсутствие ES6+**: Нет `let`, `const`, `arrow functions`, `Promise`, `class`, `async/await`, деструктуризации и методов массивов вроде `map`, `filter`, `forEach`. Любой современный JS-код вызовет синтаксическую ошибку.
2.  **Однопоточность**: Запуск тяжелого ExtendScript скрипта полностью замораживает интерфейс Premiere Pro до окончания выполнения.
3.  **Передача данных в CEP**: Результат работы `evalScript` может быть передан только в виде строки. Сложные структуры необходимо сериализовать в JSON.
4.  **Отсутствие нативного JSON**: В движке нет объекта `JSON`. Необходимо использовать библиотеку-полифилл `json2.js`.
5.  **Утечки памяти в глобальной области**: Все необъявленные переменные попадают в глобальный контекст и сохраняются между выполнениями скриптов в сессии Premiere Pro, что приводит к конфликтам и утечкам памяти.

---

## 5. Reverse Engineering и Недокументированные Возможности

### QE DOM (Quality Engineering API)
ExtendScript содержит скрытый слой API разработчиков тестирования Premiere Pro, дающий гораздо более широкие возможности (например, вставка клипов в конкретное место таймлайна, доступ к Source Monitor).
*   Активация: `app.enableQE();`
*   Доступ к QE DOM: через глобальный объект `qe`.
*   *Подробнее см. в разделе [Reverse Engineering](Reverse_Engineering.md).*

### Reflection (Рефлексия объектов)
ExtendScript предоставляет механизм интроспекции любого объекта на лету:
*   `obj.reflect`: Свойство, возвращающее объект рефлексии.
*   `obj.reflect.properties`: Список всех доступных свойств объекта.
*   `obj.reflect.methods`: Список всех доступных методов объекта.

---

## 6. Распространенные Ошибки и Антипаттерны (Anti-patterns)

*   **Антипаттерн: Загрязнение глобального пространства**
    ```javascript
    // Плохо: переменная myProject глобальна и может быть переписана другим скриптом
    myProject = app.project; 
    ```
    *Решение:* Обертывать весь код в анонимную самовызывающуюся функцию (IIFE):
    ```javascript
    (function() {
        var myProject = app.project;
    })();
    ```

*   **Антипаттерн: Использование путей в стиле OS в объектах File**
    ```javascript
    // Плохо: на Mac и Windows пути различаются, этот код не кроссплатформенный
    var file = new File("C:\\videos\\clip.mp4");
    ```
    *Решение:* Использовать пути URI-формата Adobe (`/c/videos/clip.mp4` или относительные пути) и свойство `File.fsName` для получения пути в системном формате.

---

## 7. Production-Ready Примеры Кода

### 1. Шаблон безопасного выполнения скрипта (IIFE с обработкой ошибок)
```javascript
(function() {
    try {
        if (!app.project) {
            alert("Нет открытого проекта!");
            return "ERROR: No open project";
        }
        
        var project = app.project;
        var activeSeq = project.activeSequence;
        
        if (!activeSeq) {
            alert("Нет активного эпизода (Sequence)!");
            return "ERROR: No active sequence";
        }
        
        // Основной рабочий код
        var msg = "Активный эпизод: " + activeSeq.name;
        $.writeln(msg);
        
        return "SUCCESS: " + activeSeq.name;
    } catch (err) {
        $.writeln("Ошибка: " + err.toString() + " на строке " + err.line);
        return "ERROR: " + err.toString();
    }
})();
```

### 2. Скрипт-дампер структуры любого объекта (Reflection API)
Служит для поиска скрытых методов и свойств. Запишет все доступные свойства объекта в лог-файл.
```javascript
function dumpObject(obj, fileName) {
    if (!obj || !obj.reflect) return "Not dynamic object";
    
    var file = new File(Folder.desktop.fsName + "/" + fileName + ".txt");
    file.open("w");
    
    file.writeln("=== PROPERTIES ===");
    var props = obj.reflect.properties;
    for (var i = 0; i < props.length; i++) {
        try {
            file.writeln(props[i].name + " = " + obj[props[i].name]);
        } catch (e) {
            file.writeln(props[i].name + " = [Error reading property: " + e.toString() + "]");
        }
    }
    
    file.writeln("\n=== METHODS ===");
    var methods = obj.reflect.methods;
    for (var j = 0; j < methods.length; j++) {
        file.writeln(methods[j].name + "()");
    }
    
    file.close();
    return "Dump saved to " + file.fsName;
}

// Пример использования:
// dumpObject(app.project.activeSequence, "sequence_dump");
```

---

## 8. Практические Рекомендации (Best Practices)

1.  **Всегда используйте `var`**: Из-за отсутствия `let` и `const`, забытое ключевое слово `var` автоматически превращает переменную в глобальную.
2.  **Изолируйте контекст**: Всегда используйте IIFE. Если разрабатывается комплексная библиотека, создавайте единый глобальный объект-пространство имен (например, `var MyCustomPlugin = MyCustomPlugin || {};`).
3.  **Используйте E4X для XML**: Работа с XML строками в ExtendScript намного быстрее и лаконичнее, чем регулярные выражения или кастомные парсеры:
    ```javascript
    var myXML = new XML("<data><item id='1'>Clip</item></data>");
    var itemId = myXML.item[0].@id; // Получит '1'
    ```

---

## 9. Источники (Sources & References)
*   [Adobe CEP Resources on GitHub](https://github.com/Adobe-CEP/CEP-Resources)
*   [Premiere Pro Scripting Guide (Unofficial / Community-driven docs)](https://ppro-scripting.docsforadobe.dev/)
*   [ExtendScript Toolkit documentation (Adobe)](https://www.adobe.com/devnet/scripting/estk.html)
