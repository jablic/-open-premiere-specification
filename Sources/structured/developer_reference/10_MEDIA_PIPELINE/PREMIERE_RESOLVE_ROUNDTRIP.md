# Adobe Premiere Pro ↔ DaVinci Resolve: перенос и round-trip

## Scope and evidence

Этот документ описывает interchange-пайплайн между Premiere Pro и DaVinci Resolve. Он разделяет подтверждённые возможности форматов, инструкции host applications и community troubleshooting. Версия Premiere/Resolve всегда является частью контракта; универсальная lossless-совместимость не заявляется.

## Короткий выбор формата

| Задача | Предпочтительный путь | Почему | Что не гарантируется |
|---|---|---|---|
| Picture lock из Premiere в Resolve для conform/color | Premiere FCP7 XML → Resolve XML import | Передаёт editorial cut, source references и базовую структуру | Premiere effects, transitions, merged/multicam semantics, audio automation |
| Audio turnover из Premiere | AAF с явно выбранными media options | Composition и audio tracks удобнее для audio/post systems | Полная эквивалентность plug-ins, routing и automation |
| Простая однотрековая EDL | EDL | Минимальный и широко поддерживаемый cut list | Multitrack, metadata, effects, transitions, complex time remap |
| Нейтральный pipeline tool | OTIO | Явная модель времени и adapters | Конкретный Premiere↔Resolve mapping зависит от adapter/host |
| Возврат graded media в Premiere | Resolve FCP7 XML + rendered media | XML связывает новые renders с исходной editorial структурой | Premiere-specific effects и часть audio/graphics возвращаются отдельно |

EDL — аварийный/минимальный interchange, а не универсальная замена XML/AAF. В частности, Resolve manual указывает, что при экспорте multitrack timeline в EDL экспортируется только текущий выбранный video track.

## Передача Premiere → Resolve для color/conform

### 1. Подготовка в Premiere

Перед экспортом:

1. Сохранить project и сделать immutable backup picture-lock sequence.
2. Убедиться, что media linked; Adobe прямо указывает это как prerequisite для FCP XML export.
3. Зафиксировать sequence start timecode, frame rate, resolution, audio sample rate и field/interlace policy.
4. Дублировать sequence для turnover и не менять его после экспорта.
5. По возможности удалить или отключить Premiere-only effects, transitions, time remapping, adjustment layers, MOGRTs и nested constructs, которые должны остаться в Premiere.
6. Зафиксировать список таких элементов в turnover report.
7. Для merged/multicam clips определить отдельную стратегию: flatten/render, camera-original conform или ручное восстановление. Не рассчитывать, что XML передаст исходную Premiere semantics.

### 2. Выбор файла

Для типичного picture conform используйте Premiere File → Export → Final Cut Pro XML. Adobe сообщает, что переносится только часть effects/features, некоторые audio pan/gain/level changes могут переноситься неточно, а complex effects/transitions могут не переводиться точно. Premiere создаёт FCP Translation Results log; этот log должен входить в turnover package.

Для автоматизации в UXP доступен `ProjectConverter.exportAsFinalCutProXML(sequence, outputFilePath, suppressUI)` начиная с Premiere Pro API `26.2`; он возвращает `Promise<boolean>`. Это API экспорта, а не гарантия одинакового Resolve import mapping.

### 3. Импорт в Resolve

Resolve предоставляет File → Import AAF, EDL, XML или импорт timeline из Edit page. В Load XML/AAF dialog следует явно проверить:

- какую sequence/timeline импортировать;
- master timeline start timecode;
- Automatically set project settings;
- Automatically import source clips into media pool;
- matching по filename/extension и reel/camera metadata;
- use sizing information;
- use color information;
- use drop-frame timecode;
- timeline и EDL frame rates.

Не включайте автоматическое изменение project settings без сравнения с locked Premiere sequence. Если Resolve создаёт новую timeline с неверным start timecode или frame rate, conform может выглядеть правильно на первых клипах и разъехаться дальше.

## Media conform и relink

Надёжность conform определяется не именем XML, а совпадением media identity и time extents. До импорта подготовьте:

- одинаковые или явно сопоставленные reel/tape names;
- исходные media в Media Pool Resolve;
- стабильные source filenames и extensions либо заранее определённое правило matching;
- source start/end timecode;
- frame rate и drop-frame/non-drop-frame режим;
- достаточные handles;
- одинаковую интерпретацию image sequences и audio BWF/iXML metadata.

Если Resolve не видит media, сначала отделяйте три причины: файл отсутствует в Media Pool, не совпадает reel/name, либо timecode extents не покрывают requested source range. Не лечите все случаи сменой одного checkbox.

Community reports дополнительно указывают на проблемы с merged clips, BWF/iXML start offsets и различиями в трактовке audio timecode. Это evidence level D: применяйте как troubleshooting hypotheses и подтверждайте fixture на конкретных файлах.

## Что делать в Resolve

Resolve может использовать imported timeline для color, conform и render. Если исходный Premiere timeline содержит unsupported effects, Resolve manual описывает различие:

- при XML export unsupported effects сохраняются внутренне Resolve и могут быть экспортированы обратно в output XML;
- для AAF unsupported effects могут экспортироваться, пока timeline не была re-edited;
- после re-edit AAF может быть экспортирован уже без unsupported effects.

Это не означает, что Premiere восстановит эффект визуально автоматически. Сохраняйте исходную Premiere sequence и возвращайте graded media отдельным слоем/sequence, чтобы повторно применить Premiere-only finishing.

## Resolve → Premiere: возврат graded media

Рекомендуемый базовый путь:

1. В Resolve дублировать conformed timeline.
2. Не менять editorial structure после color conform без отдельного change report.
3. Render graded clips в предсказуемый codec/container и сохранить source-to-render mapping.
4. Экспортировать FCP7 XML с references на rendered media.
5. В Premiere импортировать новый XML в отдельный bin/sequence.
6. Сверить clip count, order, source/timeline duration, start timecode и render paths.
7. Оставить оригинальный locked edit под imported graded sequence для A/B и ручного восстановления.
8. Повторно применить Premiere effects, MOGRTs, captions, adjustment layers и finishing, которые сознательно не передавались в Resolve.
9. Проверить кадры на head/tail, transitions, retimes, reframing и color management.

Resolve manual прямо описывает экспорт AAF/XML после render graded clips как способ отправить timeline обратно в originating NLE или в finishing application. Это interchange workflow, не сохранение нативной Resolve project database.

## AAF: когда он нужен

AAF полезнее XML, когда приоритетом являются audio composition, track layout и media turnover. Для AAF нужно заранее зафиксировать:

- link to existing media, copy all media, consolidate with handles или mixdown;
- audio/video inclusion;
- handle length;
- sample rate и bit depth;
- embedded/link policy;
- ожидаемое расположение media и relink procedure.

AAF Association описывает AAF как object model для essence, composition и metadata, но transparent interchange зависит от application profile. Не следует считать `.aaf` самодостаточным или автоматически online в Resolve/Premiere.

## EDL: ограничения

EDL имеет смысл для простого плоского conform: один video track, базовые cuts, source/timeline timecodes и reel names. Не используйте EDL как единственный deliverable при наличии:

- нескольких video/audio tracks;
- transitions;
- effects и keyframes;
- variable speed/time remap;
- multicam/merged/compound clips;
- markers, captions и rich metadata.

Если EDL нужен как fallback, передавайте параллельно XML/AAF и human-readable exception report.

## OTIO: роль в связующем слое

OTIO удобно использовать как проверяемую промежуточную модель для editorial metadata и time ranges. Но `fcp_xml` adapter имеет собственную feature matrix и не поддерживает transitions, audio/video effects, linear/complex speed effects и CDL. Поэтому схема `Premiere → OTIO → Resolve` добавляет ещё один lossy boundary и не должна считаться улучшением по умолчанию по сравнению с direct XML.

OTIO имеет смысл, если нужно:

- построить versioned metadata/conform service;
- нормализовать time ranges до host import;
- запустить media linker;
- провести structural diff до открытия NLE;
- поддержать несколько adapters с единым audit report.

## Validation protocol

Каждый новый pipeline должен прогоняться на fixture, содержащем:

1. два video tracks и минимум два audio tracks;
2. non-zero sequence start timecode;
3. mixed source start timecodes и drop/non-drop case;
4. gap, marker, nested/compound item;
5. transition, keyframed motion/opacity и speed change;
6. merged/multicam representative;
7. BWF audio с metadata start offset;
8. offline/relink candidate;
9. graded render с head/tail handles;
10. caption/MOGRT/adjustment-layer exception.

Сохраняйте до/после report с полями:

```text
host versions
format + exporter/importer versions
sequence/timeline settings
clip count / track count
source and timeline timecodes
reel/name/path matching result
preserved / transformed / dropped / unknown
manual repairs
visual QC result
```

Минимальная автоматическая проверка должна сравнивать не только количество клипов, но и `(source identity, source in/out, timeline in/out, rate, track, duration)`. После этого нужен визуальный QC с burn-in timecode и clip/reel labels.

## Failure triage

| Симптом | Первые проверки |
|---|---|
| Timeline импортируется, но клипы offline | Media Pool, paths, reel/name, extensions |
| Клип находится, но неверный участок | source timecode, media start offset, frame rate, handles |
| Съехал весь timeline | master start timecode, drop-frame, timeline/EDL rate |
| Неверный кадр/масштаб | source/timeline resolution, sizing information, pixel aspect |
| Стало два mono вместо stereo | audio channel interpretation и channel mapping после XML/AAF import |
| Пропали effects/transitions | format feature matrix; exception report; original locked sequence |
| Возврат в Premiere меняет duration | retime, transition overlap, handles, render frame boundaries |
| XML/AAF открывается, но результат неверен | semantic validation; форматная валидность не равна host fidelity |

## Hard rules for automation

- Не перезаписывать locked source sequence.
- Не считать успешный import доказательством conform.
- Не сравнивать только filenames; включать reel, timecode extents и rate.
- Не смешивать color transforms из Resolve с Premiere color management без зафиксированного display/render policy.
- Не переносить Premiere-only effects молча: вести dropped/unknown manifest.
- Не использовать EDL как единственный backup rich timeline.
- Не объявлять XML/AAF/OTIO round-trip lossless без fixture evidence.

## References

- [Adobe: export Premiere project as Final Cut Pro XML](https://helpx.adobe.com/premiere/desktop/render-and-export/export-files/export-a-project-as-a-final-cut-pro-xml-file.html)
- [Adobe: supported direct export formats](https://helpx.adobe.com/premiere/desktop/render-and-export/export-files/supported-export-file-formats.html)
- [Adobe Premiere UXP ProjectConverter](https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/projectconverter)
- [Blackmagic DaVinci Resolve Colorist Reference Manual — conforming projects](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_10_Reference_Manual.pdf)
- [Blackmagic DaVinci Resolve Colorist Reference Manual — exporting AAF/XML](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_11_Reference_Manual.pdf)
- [OpenTimelineIO FCP7 XML adapter feature matrix](https://github.com/OpenTimelineIO/otio-fcp-adapter)
- [AAF Association specifications](https://aafassociation.org/specs.html)
- [Blackmagic community: Premiere XML round-trip observations](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=185245)
- [Blackmagic community: relinking Premiere XML in Resolve](https://forum.blackmagicdesign.com/viewtopic.php?f=3&t=112614)
