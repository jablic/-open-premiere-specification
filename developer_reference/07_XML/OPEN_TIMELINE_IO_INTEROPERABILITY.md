# OpenTimelineIO и совместимость с Premiere Pro

## Overview

OpenTimelineIO (OTIO) — API и формат обмена для монтажной информации: порядка и длительности монтажных элементов, тайминга, треков, переходов, маркеров и ссылок на внешние медиа. OTIO не является контейнером аудио или видео: медиаданные остаются внешними по отношению к таймлайну.

Для Premiere Pro важно различать три уровня:

1. нативный `.otio` как формат модели OTIO;
2. FCP7 XML как текстовый interchange-формат, который может использоваться как мост к Premiere Pro;
3. вызов Premiere UXP `ProjectConverter.exportAsOpenTimelineIO()` — официальный экспорт последовательности в OTIO из Premiere Pro.

Это не утверждение о полной двусторонней совместимости. Любой XML/OTIO round-trip следует считать потенциально lossy, пока конкретные свойства не проверены на целевой версии Premiere Pro и используемом адаптере.

## Модель данных

Базовая иерархия OTIO:

```text
Timeline → Stack → Track → Clip / Gap / Transition
                         └→ MediaReference
```

`Clip` — экземпляр монтажа на таймлайне. `MediaReference` — ссылка на исходный медиаресурс, а не встроенный медиаконтент. Временные значения представлены через `RationalTime` и `TimeRange`; это позволяет явно хранить rate, start time и duration, но не устраняет различия в семантике NLE при импорте.

Метаданные OTIO расширяемы. Для данных, специфичных для формата или приложения, следует использовать namespaced metadata и не выдавать такие поля за переносимую часть контракта.

## Формат `.otio` и адаптеры

Нативный `.otio` — JSON-представление модели OTIO. Документация OTIO называет его единственным lossless-форматом относительно возможностей самой модели; адаптеры других форматов сохраняют только поддерживаемое ими подмножество. Поэтому `.otio` не следует автоматически считать эквивалентом Premiere project или XML-архива.

Адаптеры подключаются через plugin system. В актуальной экосистеме основной пакет OTIO содержит нативные форматы, а дополнительные адаптеры, включая `fcp_xml`, распространяются в OpenTimelineIO-Plugins/отдельных репозиториях. Наличие адаптера в списке не означает, что конкретная версия адаптера поддерживает все конструкции исходного NLE.

## FCP7 XML adapter: подтверждённая матрица

Матрица ниже относится к community adapter `OpenTimelineIO/otio-fcp-adapter`, а не к произвольному XML-экспорту Premiere Pro.

| Возможность | Поддержка адаптером |
|---|---|
| Один трек клипов | Да |
| Несколько видеотреков | Да |
| Аудиотреки и аудиоклипы | Да |
| Gap/filler | Да |
| Маркеры | Да |
| Nesting | Да |
| Transitions | Нет |
| Audio/video effects | Нет |
| Linear speed effects | Нет |
| Complex/fancy speed effects | Нет |
| Color Decision List (CDL) | Нет |
| Image-sequence reference | Только запись (write-only) |

Следствие для Premiere-пайплайна: экспорт, преобразование через OTIO и обратный импорт нельзя объявлять безопасным для переходов, эффектов, speed remapping, CDL и image sequences без отдельного теста. Несовместимость может проявиться как потеря, упрощение или изменение поведения, а не обязательно как ошибка парсинга.

## Premiere Pro UXP

Официальный Premiere UXP API документирует статический метод:

```ts
ProjectConverter.exportAsOpenTimelineIO(
  sequence: Sequence,
  outputFilePath: string,
  suppressUI: boolean,
): Promise<boolean>
```

Метод доступен начиная с Premiere Pro API `26.2` согласно reference page `ProjectConverter`. Возвращаемое `Promise<boolean>` сообщает результат операции экспорта, но опубликованная сигнатура не описывает содержимое OTIO, mapping каждого типа track item или гарантию round-trip. Эти свойства следует считать **Not documented** до появления соответствующей спецификации или проверяемого sample behavior.

Официальный sample `uxp-premiere-pro-samples` включает модуль `projectConverter.ts` и покрывает экспорт как Final Cut Pro XML, так и OpenTimelineIO. Sample полезен как executable reference вызова API, но не заменяет контрактную документацию формата и не доказывает lossless interoperability.

Минимальный рабочий паттерн должен проверять boolean-результат и существование выходного файла после завершения Promise:

```ts
const ok = await ProjectConverter.exportAsOpenTimelineIO(
  sequence,
  outputFilePath,
  true,
);

if (!ok) {
  throw new Error("Premiere Pro did not complete OTIO export");
}
```

Тип `Sequence`, условия валидности `outputFilePath`, перечень экспортируемых объектов и причины `false` в доступной reference page отдельно не раскрыты: **Not documented**.

## Interoperability contract

Для production round-trip фиксируйте минимум:

- версию Premiere Pro и UXP API;
- версию OTIO и `fcp_xml` adapter;
- исходный timeline rate и используемые `RationalTime`/`TimeRange`;
- media reference URLs и правила их нормализации;
- поддерживаемые и намеренно отброшенные свойства;
- post-import diff по clip order, source range, track placement, markers и durations;
- визуальную проверку переходов, эффектов, speed changes и audio channel mapping.

Не следует предполагать, что:

- XML, созданный Premiere Pro, идентичен XML, который способен записать OTIO adapter;
- linking audio/video сохранится автоматически;
- отсутствие `source_range` будет корректно обработано каждым адаптером;
- неизвестные XML-узлы переживут round-trip без явного passthrough механизма;
- наличие `exportAsOpenTimelineIO` означает наличие симметричного официального OTIO import API.

Последние пять пунктов — ограничения/риски, зафиксированные источниками и текущей документацией; поведение для конкретной версии Premiere Pro нужно подтверждать fixture-тестом.

## Safe test fixture

Перед production-переносом создайте маленькую последовательность с:

1. двумя видеотреками и одним gap;
2. аудиотреком;
3. marker;
4. nested sequence;
5. transition, effect и speed change как отдельными тестовыми элементами;
6. media reference с известным `available_range`.

Экспортируйте её из Premiere Pro в OTIO, прочитайте OTIO соответствующим adapter, затем сравните структуру и отдельно откройте результат в целевом NLE. Неподдержанные элементы должны быть явно перечислены в отчёте, а не silently accepted.

## Known Issues

- FCP7 XML adapter не поддерживает transitions, audio/video effects, linear/complex speed effects и CDL.
- Image sequence reference у adapter имеет режим write-only.
- FCP XML/EDL adapter может требовать заданный `MediaReference.available_range`; отсутствие `Clip.source_range` уже приводило к ошибкам записи в опубликованных issue.
- Сохранение audio/video links и channel mapping не следует считать гарантированным; community discussions указывают на ограничения текущего adapter.
- `ProjectConverter.exportAsOpenTimelineIO` документирует экспорт, но не полный round-trip contract.

## References

- [OpenTimelineIO repository and overview](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) — official project repository.
- [OpenTimelineIO adapters](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/adapters.md) — native and plugin adapters.
- [Writing an OTIO adapter](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/write-an-adapter.md) — adapter contract and lossless/lossy distinction.
- [FCP7 XML adapter](https://github.com/OpenTimelineIO/otio-fcp-adapter) — feature matrix and supported limitations.
- [Premiere Pro ProjectConverter](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/projectconverter) — official UXP export methods and version markers.
- [Adobe UXP Premiere samples](https://github.com/AdobeDocs/uxp-premiere-pro-samples) — official sample repository; `premiere-api` includes project conversion examples.
- [Premiere UXP starters and samples](https://developer.adobe.com/premiere-pro/uxp/resources/starters-samples/) — Adobe-maintained entry point to samples.
- [OTIO issue: missing source ranges](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues/1096) — community-reported adapter failure mode.
- [OTIO discussion: audio/video links](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/discussions/1271) — community evidence; not an official contract.
