# Interoperability: Premiere Pro и другие монтажные системы

## Основной принцип

Ни один interchange format не переносит полную семантику native project. Выбор формата определяется тем, что нужно сохранить: editorial decisions, audio composition, media essence, metadata, effects или возможность ручного восстановления.

| Направление | Формат/слой | Сильная сторона | Главный риск |
|---|---|---|---|
| Premiere ↔ Final Cut Pro / совместимые NLE | FCP7 XML / XMEML | Текстовый, inspectable, удобен для clip/track/timing обмена | Версия XML и application-specific extensions; неполный перенос effects и UI state |
| Premiere ↔ Final Cut Pro | FCPXML | Apple-специфичная современная модель resources/events/projects | Не является native library/project; DTD-valid документ всё ещё может быть отвергнут из-за invalid data |
| Premiere ↔ Avid / audio/post systems | AAF | Object model для composition, metadata и essence references | Реальная поддержка зависит от application profile, media mode и handles |
| Premiere ↔ Resolve / pipeline tools | OTIO | Нейтральная editorial модель и plugin adapters | Adapter mapping lossy; FCP7 adapter не поддерживает ряд effects/speed/transition cases |
| Premiere ↔ proprietary native project | Native project API/file | Максимум application-specific fidelity | Высокая version coupling и ограниченная portability |

Таблица — инженерная классификация, а не обещание совместимости конкретной пары версий.

## FCP7 XML / XMEML

Apple’s archived XMEML reference описывает `xmeml`, `project`, `bin`, `sequence`, media tracks, linking, transitions, effects и import options. Документ retired, поэтому его следует применять как format reference, а не как гарантию поведения современных Final Cut Pro или Premiere.

Для XML трансформаций сохраняйте неизвестные узлы и атрибуты, если целью является round-trip. Проверяйте DTD/schema, но не путайте структурную валидность с импортируемостью: application может отвергнуть формально допустимый документ из-за семантически invalid data.

## FCPXML

Актуальная Apple reference определяет FCPXML как формат обмена media, metadata, assets, projects и editing decisions. FCPXML 1.9 требует Final Cut Pro 10.4.9 или новее; актуальная DTD page указывает FCPXML 1.10. Версию документа и целевую версию host нужно хранить явно.

Apple прямо указывает, что FCPXML не является заменой native Final Cut Pro library bundle. Следовательно, экспорт из Premiere в XML — delivery/interchange artifact, не резервная копия проекта.

## AAF

AAF Association/AMWA описывает AAF как cross-platform multimedia interchange format, который может содержать essence data, composition information и metadata. AAF предоставляет object specification, stored/container specification и SDK reference implementation; application-specific extensions и profile support остаются значимыми.

Практическое различие media modes подтверждается Avid documentation: AAF может ссылаться на существующие media, копировать весь media, consolidate с handles или делать video mixdown. Перед передачей в другую систему нужно фиксировать выбранный mode, handle length, audio/video inclusion и ожидаемое расположение `Avid MediaFiles`.

Для Premiere↔Avid workflow AAF нельзя тестировать только по наличию `.aaf`: проверяйте online state, source timecodes, tracks, handles, audio effects/mixdown и relink destination.

## OTIO

OTIO предоставляет neutral editorial model, а не media container. Для Premiere workflow особенно важны:

- `Timeline → Stack → Track → Clip/Gap/Transition`;
- `Clip` отдельно от `MediaReference`;
- `RationalTime`/`TimeRange` с явным rate;
- adapters как отдельный compatibility layer;
- namespaced metadata для application-specific identifiers.

Официальный `fcp_xml` adapter поддерживает multiple video tracks, audio tracks, gaps, markers и nesting, но не поддерживает transitions, audio/video effects, linear/complex speed effects и CDL; image-sequence reference имеет write-only поддержку. Это ограничения adapter, не всего OTIO и не доказательство ограничений Premiere XML export.

## DaVinci Resolve

Blackmagic официально документирует scripting API в Developer documentation, доступной из Resolve через Help → Documentation → Developer; опубликованные release notes указывают расширение scripting API по версиям. Для interoperable pipeline это означает, что Resolve scripting и XML/AAF/OTIO interchange следует рассматривать как разные поверхности: скрипт управляет host, а interchange переносит данные между host’ами.

Конкретный Resolve import/export mapping, включая effects, transitions, multicam, audio channel layouts и speed changes, должен быть подтверждён fixture на целевой версии Resolve. При отсутствии такой проверки в reference писать `Not documented`.

## Verification matrix

Для каждого направления создайте fixture с:

1. двумя video tracks и одним audio track;
2. trim и non-zero source start;
3. gap и marker;
4. nested sequence/compound composition;
5. transition, effect, speed change и keyframes;
6. linked audio/video и multi-channel audio;
7. external media с handles и известным timecode.

Сравнивайте до/после:

- clip identity и порядок;
- source/timeline ranges и rate;
- track kind/index;
- markers;
- transitions/effects/speed;
- audio channel mapping;
- media paths, online state и handles;
- визуальный результат и manual repair count.

Результат оформляйте как capability matrix с колонками `preserved`, `transformed`, `dropped`, `unknown`, `verified version` и `evidence source`.

## References

- [Apple FCPXML reference](https://developer.apple.com/documentation/professional-video-applications/fcpxml-reference)
- [Apple FCPXML DTD](https://developer.apple.com/documentation/professional-video-applications/document-type-definition)
- [Apple archived XMEML reference](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/)
- [AAF Association specifications](https://aafassociation.org/specs.html)
- [AAF Object Specification](https://aafassociation.org/specs/object_spec.html)
- [Avid: exporting AAF](https://kb.avid.com/pkb/articles/en_US/How_To/How-to-export-an-AAF)
- [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO)
- [OpenTimelineIO FCP7 XML adapter](https://github.com/OpenTimelineIO/otio-fcp-adapter)
- [Blackmagic Resolve scripting API note](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_17_New_Features_Guide.pdf)
