# Документация VFX List Export

Phase 0 Resolve contract: [docs/PHASE_0_RESOLVE_FIXTURE_CONTRACT.md](docs/PHASE_0_RESOLVE_FIXTURE_CONTRACT.md).

Актуально для версии **0.7.92**.

## Основные документы

- [Итоговое резюме проекта](PROJECT_SUMMARY.md)
- [Назначение и устройство продукта](PRODUCT_GUIDE.md)
- [Справочник функций](FUNCTION_REFERENCE.md)
- [Ошибки, ограничения и уроки разработки](KNOWN_ISSUES_AND_LESSONS.md)
- [Разработка и выпуск версии](DEVELOPMENT_AND_RELEASE.md)
- [Алгоритмы таймкода активной секвенции](TIMECODE_ALGORITHMS.md)
- [Глубокая ревизия кода 2026-08-16](CODE_AUDIT_2026-08-16.md)
- [Глубокая ревизия кода 2026-09-02](CODE_AUDIT_2026-09-02.md)
- [Техническая спецификация DaVinci Resolve](DAVINCI_RESOLVE_VFX_EXPORT_LIST_SPEC_2026-09-02.md)
- [Разбор исторических материалов `files.zip`](SOURCE_MATERIALS_REVIEW.md)

## Инструкции по рабочим блокам

1. [VFX List](functions/01-vfx-list.md)
2. [Video references](functions/02-video-references.md)
3. [Convert](functions/03-convert.md)
4. [Rename & renumber](functions/04-rename-renumber.md)
5. [Check Prmst/Hires](functions/05-import-and-check.md)
6. [Results, журнал и диагностика](functions/06-results-and-diagnostics.md)

## Быстрый маршрут

1. Откройте монтажную секвенцию в Premiere Pro.
2. В **VFX List** выберите источник Shot ID.
3. Нажмите **Scan / preview** и проверьте Shot ID, TC In и TC Out.
4. Выберите колонки, footage track, формат и параметры кадров.
5. Нажмите **Export VFX list**.
6. Для turnover дополнительно экспортируйте reference movies в блоке 2.
7. При отклонениях раскройте **Process log**, нажмите **Copy** и приложите журнал к описанию проблемы.
