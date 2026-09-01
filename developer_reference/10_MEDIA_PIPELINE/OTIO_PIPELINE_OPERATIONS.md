# OTIO в media pipeline: время, relink и bundles

## Назначение

Эта глава фиксирует операционные правила из официального репозитория OpenTimelineIO, полезные для инструментов вокруг Premiere Pro. Она не объявляет OTIO заменой Premiere project и не расширяет его контракт сведениями, которых нет в источниках.

## Структура и identity

OTIO-файл сериализуется как дерево вложенных объектов. В tree-модели нет object instancing: если один и тот же media reference используется несколькими клипами, в сериализованном дереве появляются соответствующие копии объектов. Это важно для AI-инструментов и diff-пайплайнов: нельзя автоматически трактовать совпадающий JSON-фрагмент как shared object identity.

Для операций, требующих стабильной идентичности, храните собственный production identifier в namespaced metadata и не подменяйте его позицией узла или именем клипа. При преобразовании в XML проверяйте, какой идентификатор реально поддерживает целевой формат.

## Временные диапазоны

`RationalTime` хранит `value` и `rate`. `TimeRange` состоит из `start_time` и `duration`. Для клипа необходимо различать:

| Понятие | Смысл |
|---|---|
| `MediaReference.available_range` | Известный диапазон медиа, доступный по ссылке. Может быть `None`, если файл отсутствует или дорого проверяется. |
| `Clip.source_range` | Обрезанный диапазон исходного медиа, используемый данным экземпляром клипа. |
| `Clip.trimmed_range()` | Вычисляемый диапазон использованного материала; требует хотя бы `source_range` или `available_range`. |
| `duration()` | Длительность объекта/композиции после учёта вложенных элементов и trim. |

OTIO не выполняет автоматический snap или verification, если `source_range` выходит за пределы `available_range`. Downstream application может обработать такую ситуацию по-своему. Для Premiere interchange это означает, что валидатор должен обнаруживать такие диапазоны до экспорта, а не рассчитывать на исправление адаптером.

Для timecode и кадров нельзя смешивать rates без явного преобразования. Сначала нормализуйте временную базу, затем сравнивайте `RationalTime`; сравнение только числового `value` без `rate` некорректно.

## Media Linker и conform

OTIO отделяет чтение timeline от разрешения media references. Media Linker запускается после adapter и преобразует ссылки в действительные studio-specific references. Это предпочтительнее, чем зашивать правила конкретного хранилища в общий XML/OTIO parser.

Для conform-пайплайна:

1. прочитать timeline adapter’ом;
2. найти клипы через traversal (`find_clips()` или эквивалентный обход);
3. разрешить media по production metadata/asset database;
4. заменить `media_reference` на `ExternalReference` с `target_url`;
5. сохранить неизвестный `available_range` как `None`, если медиаданные не были проверены;
6. записать результат и проверить число клипов/ссылок.

Сопоставление только по `clip.name` допустимо как демонстрационный fallback, но не как production identity: официальный пример conform прямо указывает, что в студии лучше использовать asset-management metadata и shot identifier.

```python
import opentimelineio as otio

timeline = otio.adapters.read_from_file(input_path)

for clip in timeline.find_clips():
    media_path = resolve_from_asset_database(clip.metadata, clip.name)
    if media_path:
        clip.media_reference = otio.schema.ExternalReference(
            target_url="file://" + media_path,
            available_range=None,
        )

otio.adapters.write_to_file(timeline, output_path)
```

`resolve_from_asset_database` здесь намеренно является внешней функцией: OTIO не знает production storage schema.

## OTIOZ и OTIOD bundles

OTIOD — directory bundle, OTIOZ — zip bundle. Оба содержат `content.otio`; OTIOZ также содержит `version.txt` и плоскую директорию `media/`. Bundle не кодирует и не декодирует медиа: исходные файлы просто упаковываются.

Ключевые ограничения:

- `ExternalReference.target_url` должен указывать на локально доступный файл или использовать допустимую relative path форму;
- media namespace плоский, поэтому basenames файлов должны быть уникальны;
- при чтении по умолчанию разбирается `content.otio`, а media не декодируется;
- OTIOD может преобразовать media references в absolute paths через `absolute_media_reference_paths`;
- policy `ErrorIfNotFile` останавливает bundle при непредставимом файле;
- `MissingIfNotFile` заменяет такие ссылки на `MissingReference`, сохраняя исходную ссылку в metadata;
- `AllMissing` заменяет все references на `MissingReference` и помещает bundle без media.

Для Premiere turnover bundle следует заранее проверять уникальность basenames и явно выбирать media policy. Нельзя считать `.otioz` self-contained архивом, если использована политика `AllMissing` или references не указывают на локальные файлы.

## `otiotool` как проверочный слой

Официальный `otiotool` умеет читать файлы через adapter plugins, выводить статистику и перечисления, фильтровать tracks/clips, удалять transitions, flatten’ить tracks, выполнять verify-media и relink по правилам инструмента. Это удобный smoke-test перед передачей OTIO в Premiere, но операции, меняющие timeline, должны выполняться на копии.

Рекомендуемый диагностический проход:

```text
otiotool -i timeline.otio --stats --list-tracks --list-clips
otiotool -i timeline.otio --verify-media
```

Набор проверок не заменяет импорт в Premiere Pro: `otiotool` проверяет модель OTIO и доступность ссылок, а не интерпретацию всех свойств Premiere.

## Plugin discovery

Переменные plugin configuration должны быть заданы до импорта Python-библиотеки OTIO:

- `OTIO_PLUGIN_MANIFEST_PATH` — список путей к plugin manifests; разделитель `:` на POSIX и `;` на Windows;
- `OTIO_DEFAULT_MEDIA_LINKER` — имя linker’а, запускаемого после чтения;
- `OTIO_DISABLE_ENTRYPOINTS_PLUGINS=1` — отключает discovery через Python entry points;
- `OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL` — default downgrade target для записи, если явный target version не передан.

Это runtime configuration Python binding’а. В официальной документации указано, что C++ library не использует эти environment variables. Значения должны быть частью воспроизводимого pipeline manifest, иначе один и тот же `.otio` может обрабатываться разными наборами plugins.

## Premiere-specific boundary

OTIO может быть безопасным промежуточным представлением editorial cut information, но mapping к Premiere остаётся adapter/host-specific. Перед round-trip фиксируйте:

- rate и диапазоны каждого клипа;
- наличие `None` в `available_range`;
- media policy и правила relink;
- plugin manifests и версии adapters;
- уникальность media basenames для bundle;
- количество clips/tracks/markers до и после преобразования.

Любые утверждения о Premiere import, сохранении linking, effects или transitions должны подтверждаться отдельными Adobe/adapter источниками и fixture-тестом.

## References

- [OTIO repository README](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/README.md)
- [Timeline structure](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-timeline-structure.md)
- [OTIO file format specification](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-file-format-specification.md)
- [OTIO file bundles](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-filebundles.md)
- [OTIO environment variables](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-env-variables.md)
- [OTIO plugins](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otio-plugins.md)
- [OTIO conform example](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/examples/conform.py)
- [OTIO timing summary example](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/examples/summarize_timing.py)
- [OTIO `otiotool` tutorial](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/otiotool.md)
