---
id: best-practices
title: Best Practices (Production)
category: meta
status: current
stability: active
doc_status: partial
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript, typescript]
tags: [best-practices, error-handling, version-aware, validation, utf-8, non-destructive]
related: [extendscript-core, essential-graphics-mogrt-text, export-rendering-media-encoder, uxp, 00-technology-status-matrix]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/
---

# Best Practices (Production)

## TL;DR
- The cross-cutting rules every generated script must follow. **Partially seeded.**
- Validate the whole chain (project→sequence→track→clip→component→property→JSON parse→setValue). Be version-aware. UTF-8. Non-destructive.

## Status & Lifecycle
- `current` guidance applicable across runtimes. See `00-technology-status-matrix`.

## Architecture
N/A — this is a checklist doc. **STUB.**

## API Surface
N/A. **STUB.**

## Working Examples
**Validation chain (ExtendScript):** check `app.project`, `activeSequence`, target track exists, `clips.numItems`, component found, `getParamForDisplayName` non-null, `JSON.parse` in try/catch, `setValue` success. See `extendscript-core` examples. **STUB: codified guard helpers.**

## Limitations
N/A.

## Common Errors & Gotchas
**Version-aware musts:** Time object vs raw number (14.1+); fillColor 0–255 vs 0–1; **HEVC block at 25.5**; Source-Text caching-bug regressions; collections use `.numItems`. Bundle **json2.js** for ExtendScript; never trust the ambient global `JSON`. For UXP wrap mutations in `executeTransaction` with undo strings. **STUB.**

## Workarounds
Always force a render to flush the MOGRT text cache when needed (see `essential-graphics-mogrt-text`). **STUB.**

## Migration
Prefer UXP for new systems; ExtendScript only for legacy/compat. **STUB.**

## Cross-References
- `extendscript-core`
- `essential-graphics-mogrt-text`
- `export-rendering-media-encoder`
- `uxp`
- `00-technology-status-matrix`

## Sources
- https://ppro-scripting.docsforadobe.dev/

