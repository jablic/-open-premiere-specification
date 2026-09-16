# VFX EXPORT LIST для DaVinci Resolve — техническая спецификация

Версия документа: 1.0  
Дата: 2026-09-02  
Статус: архитектурное задание и критерии приёмки; реализация Resolve-адаптера ещё не начата.

## 1. Цель и границы

Создать Resolve Studio Workflow Integration Plugin с тем же производственным
результатом, что и текущий VFX List Export для Premiere: sequence/timeline →
проверенный shot model → VFX-таблица → thumbnails/reference movies → conform и
контроль результата.

Это не перенос CEP или ExtendScript. Общий доменный слой должен быть отделён от
host-адаптеров Premiere и Resolve.

## 2. Зафиксированный выбор платформы

### Production

**Electron Workflow Integration Plugin** — основной вариант для macOS и Windows
в Resolve Studio. Он даёт полноценный HTML/CSS/JavaScript-интерфейс и вызывает
Resolve API через WorkflowIntegration bridge. Resolve 20.1 официально обновил
поддержку Electron 36.3.2 для Workflow Integrations.

### Prototype/Linux fallback

Python/Lua Workflow Integration script + Fusion UIManager. Это допустимый
fallback, но UI будет отдельным Qt-окном и не повторит текущую панель по уровню
UX. На Linux HTML/Electron Workflow Integration не следует считать доступным.

### Не использовать как основу

- OpenFX — предназначен для image effects, не для project-management панели.
- Fuse — Fusion-инструмент, не общий timeline/conform API.
- Только внешний браузер — запасной режим, если Studio/Workflow Integration
  недоступен; не основной продукт.

Официальные материалы: [Fusion Scripting Guide](https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf),
[Resolve 20.1 New Features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20.1_New_Features_Guide.pdf?_v=1756105210000),
[Studio Features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_Features.pdf?_v=1658732410000).

## 3. Целевая архитектура

```text
Workflow Integration Electron UI
        │
        ├── local command/state protocol
        │
        ├── Resolve adapter (JavaScript/Python API)
        │       ├── project/timeline
        │       ├── markers/items/media pool
        │       └── render/conform
        │
        └── vfx-core (shared, host-neutral)
                ├── integer-frame timecode
                ├── shot model and validation
                ├── columns/config
                ├── CSV/XLSX/PDF
                └── tracker bridges
```

### Репозитории/каталоги

```text
resolve-vfx-export/
  plugin/                    # manifest, Electron main/preload/renderer
  resolve_adapter/           # Resolve API calls only
  vfx_core/                  # pure Python, unit-testable
  bridge/                    # XLSX/PDF/tracker/media helpers
  presets/                   # Resolve render/Fusion presets
  tests/fixtures/resolve/    # projects, exports, expected manifests
  docs/
```

`vfx_core` не должен импортировать Resolve, Premiere, Electron или UI-модули.

## 4. Функциональный состав

### Block 1 — VFX List

Источники Shot ID:

- timeline markers: Name или Comments;
- subtitle/caption track;
- Fusion/Text+ plates;
- внешний SRT.

Результат:

- нормализованный список shots;
- TC IN/OUT, duration frames/sec;
- source metadata;
- выбранные колонки;
- CSV/TXT/HTML/XLSX/PDF;
- thumbnails по shot ID.

Правило: Scan/Preview не изменяет timeline и project.

### Block 2 — Video references (PRMST)

Только per-shot video previews:

- Match sequence;
- 4K UHD, Full HD, HD 720p, 480p;
- bitrate;
- audio on/off;
- captions burn-in on/off;
- Direct render или Resolve render queue;
- output folder с collision-safe именами.

Результат каждого render job фиксируется в manifest: shot ID, requested range,
actual range, raster, fps, codec, path, status, warning.

### Block 3 — Convert

Поддержать матрицу:

- Markers → Captions;
- Markers → Fusion/Text+ plates;
- Captions → Markers;
- Text+ plates → Markers.

Если Resolve API не даёт безопасной native-записи, использовать sidecar SRT или
сгенерированный Fusion Title и явно сообщать, что native item не изменён.

### Block 4 — Rename & renumber

- audit конфликтов;
- маска Shot ID;
- numeric order;
- range IN/OUT;
- preview-first;
- explicit Apply;
- mapping CSV Old ID → New ID → TC IN;
- revert из mapping.

Write-path обязан быть fail-closed: если список markers/items прочитан неполно,
запись не начинается.

### Block 5 — Check Prmst/Hires

Порядок UI:

1. Video source: disk folder или existing Media Pool folder;
2. Check mode: embedded timecode или filename;
3. video-extension checkbox filter;
4. track/handles/options;
5. Conform to timeline.

Результат: imported/reused media, placed timeline items, per-shot status и
diagnostic report. Повторный запуск не должен создавать дубли bins или media,
если совпадает stable path/hash.

## 5. Таймкодный контракт

### Источники истины

Для активной timeline получить и сохранить snapshot:

```text
sequence_id
sequence_name
fps_exact
nominal_fps
drop_frame / non_drop
timeline_start_frame
timeline_start_timecode
duration_frames
width / height
```

### Нормализация

1. Любой displayed TC сначала разбирается в integer absolute frame.
2. Ruler start TC переводится в `timeline_start_frame`.
3. Relative timeline position: `absolute_frame - timeline_start_frame`.
4. Report TC IN/OUT снова форматируются с добавлением start frame.
5. `TC OUT` в отчёте — последний включённый кадр.
6. Render range — `[in_frame, out_frame + 1)`.
7. Embedded TC conform сравнивает абсолютные sequence frames, а не строки.

Запрещено смешивать seconds и frames внутри сравнений. Seconds используются
только на границе API Resolve; внутреннее состояние — frames.

### Drop-frame

DF допустим только для 29.97 и 59.94. Неверные skipped labels блокируются.
Для 23.976 используется non-drop display, даже если пользователь визуально
ожидает «24».

### Проверки

- round-trip `frame → TC → frame`;
- sequence starts 01:00:00:00, 02:00:00:00, 03:00:00:00;
- 23.976/24/25/29.97 DF/NDF/30/50/59.94 DF/NDF/60;
- marker crossing start/end;
- render range off-by-one;
- negative/empty/out-of-duration values.

## 6. Алгоритм построения shot model

1. Считать immutable timeline snapshot.
2. Получить markers/items через API и проверить полноту enumeration.
3. Нормализовать каждый объект в `ShotRef`:

```text
id, source, start_frame, end_frame_exclusive,
duration_frames, track, source_path, source_in_frame,
source_out_frame, fps, sequence_id
```

4. Удалить/объединить элементы только по явно выбранным правилам UI.
5. Проверить duplicate IDs, invalid ranges, missing source and collisions.
6. Сформировать immutable `ShotList`.
7. Все экспортёры и conform работают только от этого snapshot.

Это предотвращает ситуацию, когда timeline меняется между построением таблицы,
рендером и импортом.

## 7. Алгоритм reference export

1. Получить timeline snapshot и shot list.
2. Для каждого shot вычислить frame range `[start, endExclusive)`.
3. Преобразовать range в Resolve render settings.
4. Применить raster mode:
   - Match sequence → sequence width/height;
   - standard preset → exact target dimensions;
   - custom → validated width/height/bitrate.
5. Установить exact FPS активной timeline.
6. Создать collision-safe output path.
7. Добавить render job.
8. Сохранить requested manifest до запуска queue.
9. Отслеживать job status.
10. После завершения проверить наличие файла и, если доступно, metadata.
11. Сформировать report requested-vs-actual.

Если Resolve не позволяет надёжно задавать разные ranges в одной очереди,
использовать последовательную постановку jobs или временные render timelines.

## 8. Алгоритм conform

### Embedded timecode

1. Просканировать выбранную папку.
2. Для каждого media item получить embedded start TC и fps.
3. Перевести TC в absolute frame с учётом sequence start.
4. Сопоставить с shot manifest по `(sequence_id, start_frame, duration/fallback)`. 
5. Проверить fps, source duration, handles и track.
6. Импортировать только отсутствующие media items.
7. Поместить item в target video track на `start_frame`.
8. Сравнить фактическую позицию с ожидаемой.

### Filename

1. Нормализовать basename без расширения.
2. Сопоставить с Shot ID через exact match.
3. При collision остановить conform до ручного выбора.
4. Использовать embedded/source TC только как дополнительную проверку.

Нельзя считать совпадение filename достаточным доказательством правильной
позиции на timeline.

## 9. API-контракты Resolve adapter

Минимальные методы:

```python
get_active_project() -> ProjectSnapshot
get_active_timeline() -> TimelineSnapshot
get_markers(timeline) -> CompleteResult[list[MarkerRef]]
get_timeline_items(timeline, track_filter) -> CompleteResult[list[ItemRef]]
import_media(paths, media_pool_folder) -> ImportResult
find_or_create_media_pool_folder(path_or_name) -> FolderRef
add_render_job(timeline, settings, frame_range) -> RenderJobRef
start_render() -> None
get_render_status(job) -> RenderStatus
place_clip(item, track, start_frame, source_in, source_out) -> PlaceResult
```

Каждый метод обязан возвращать structured result с `status`, `warnings`,
`errors`, `source`, `api_version` и `snapshot_id`.

## 10. Безопасность и идемпотентность

- Не менять timeline до нажатия Apply/Conform.
- Не перезаписывать существующие файлы без явного режима overwrite.
- Не создавать дубликаты Media Pool bins.
- Все операции записывать в JSONL process log.
- Для каждой write-операции иметь dry-run/preview.
- При неполном API-ответе — stop, а не best-effort write.
- Python зависимости ставить в content-addressed isolated runtime.

## 11. План реализации

### Phase 0 — fixture contract

Собрать 4 Resolve Studio fixtures: 24 fps start 01h, 24 fps start 03h,
23.976 DF/NDF-equivalent test, mixed tracks/markers. Зафиксировать expected
JSON snapshots. Без этого нельзя утверждать live-совместимость.

### Phase 1 — vfx-core

Перенести timecode, shot model, columns, config, CSV/XLSX/PDF, collision logic.
Добиться полной работы без Resolve.

### Phase 2 — read-only Resolve adapter

Active project/timeline, settings, markers, timeline items, Media Pool folders.
Реализовать Diagnostics и Block 1 preview.

### Phase 3 — Workflow Integration UI

Перенести существующую panel UX, очередь команд, progress, Results и logs.

### Phase 4 — write operations

Rename, marker color, Convert, Fusion plates, mapping/revert. Каждый write-path
с preview и fail-closed guard.

### Phase 5 — render/export

Block 2, render presets, per-shot jobs, audio/captions, actual-vs-requested
verification.

### Phase 6 — conform

Disk/project-folder source, embedded TC, filename match, handles, idempotent
re-run and mismatch report.

### Phase 7 — packaging and release

Installer, plugin manifest, macOS/Windows paths, Studio compatibility matrix,
signature/package checks, documentation and live smoke.

## 12. Критерии приёмки

Инструмент считается рабочим только если:

- все 5 блоков выполняют documented happy path в Resolve Studio;
- TC IN/OUT совпадает с timeline frame snapshot при стартах 01/02/03h;
- 20+ render cases дают ожидаемый raster/fps/bitrate/audio/caption state;
- conform embedded-TC и filename mode проходят на реальных media fixtures;
- повторный запуск не создаёт дубликатов;
- incomplete enumeration блокирует write;
- Direct/render queue results проверяются по фактическому output;
- XLSX/PDF совпадают с shot model;
- installer запускает panel через `Workspace → Workflow Integrations`;
- smoke-тесты выполнены на целевых версиях Resolve Studio.

## 13. Что нельзя заявлять без live-проверки

- Полную эквивалентность Premiere EPR и Resolve render settings.
- Работоспособность native caption burn-in на всех версиях Resolve.
- Идентичное редактирование MOGRT — нужен Fusion-аналог.
- Доступность Workflow Integration в App Store-версии.
- Linux HTML panel.
- Корректность embedded TC для каждого codec/container без media fixtures.

## 14. Оптимальный первый исполняемый результат

Первый production milestone: **Resolve Studio Block 1 + Block 2 read/render
preview** на Electron Workflow Integration, с общим `vfx_core` и сохранёнными
Python XLSX/PDF bridges. После подтверждения таймкода и per-shot render
переходить к Convert/Rename, затем к Conform.

Такой порядок минимизирует риск: сначала проверяются самые ценные и наиболее
переносимые функции, а API-зависимые write/conform операции не маскируются под
готовую совместимость.
