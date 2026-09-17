---
id: uxp
title: UXP (Unified Extensibility Platform)
category: ui-extensibility
status: current
stability: active
doc_status: partial
introduced: "GR in Premiere 25.6 (beta Dec 2024)"
deprecated: null
eol: null
min_premiere_version: 25.6
api_namespace: premierepro
languages: [javascript, typescript]
tags: [uxp, premierepro, manifest-v5, udt, spectrum, async, executeTransaction, hybrid-plugin, uxpaddon]
related: [extendscript-core, cep, cpp-native-sdk, panels, 00-technology-status-matrix]
supersedes: [extendscript-core, cep]
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/
  - https://github.com/AdobeDocs/uxp-premiere-pro-samples
  - https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/
---

# UXP (Unified Extensibility Platform)

## TL;DR
- The **current** extensibility platform: GR in **Premiere 25.6** (Dec 2025). **Partially seeded — expand.**
- No Chromium, no `CSInterface` bridge — one runtime. **DOM methods are async (Promises, `await`).**
- **Incomplete surface**: no MOGRT text-blob parity, early builds lacked sequence-frame-rate getter, some panel hangs. Native bits → **UXP Hybrid `.uxpaddon`** or C++ PrSDK.

## Status & Lifecycle
- GR in **25.6**, bundling **UXP v8.1**. Only 25.6+/2026 users can run UXP plugins.
- Adobe: 1:1 CEP/ExtendScript parity **not intended**. Gate features on Premiere + UXP version pairs.
- See `00-technology-status-matrix`.

## Architecture
Single JS engine in-process. `require('premierepro')` for the DOM; `require('uxp')`/`fs`/`os` for core; Spectrum Web Components for UI. Manifest v5 (`manifest.json`). Optional C++ **Hybrid** module (`.uxpaddon`) for native/perf work. **STUB: runtime + permission model diagram.**

## API Surface
DOM (async): `project.importFiles(...)`, `createSequenceFromMedia`, `createSequenceWithPresetPath`, `executeTransaction(cb, undoString)`, `exportAsFinalCutProXML`, `SequenceEditor.createInsert/Overwrite/Clone/RemoveItems actions` (25.0+), markers, metadata, effects, keyframes, transcripts, AAF/FCPXML/OTIO `ProjectConverter`, `Preset` object, `TickTime.alignToFrame`/`alignToNearestFrame`. Properties get/set are **sync**. **STUB: full class list.**

## Working Examples
```js
// UXP (modern JS) — Premiere 25.6+
const ppro = require('premierepro');
const project = await ppro.Project.getActiveProject();
const seq = await project.getActiveSequence();
await project.executeTransaction((tx) => { /* actions */ }, 'My edit');
```
**STUB: import, sequence-edit actions, marker, export examples.**

## Limitations
No MOGRT text-blob parity (text-injection stays on ExtendScript/CEP). Early builds lacked a sequence-frame-rate getter. Stock-panel hang in some UXP panels. Spectrum Web Components not fully supported in Premiere yet. **STUB.**

## Common Errors & Gotchas
Forgetting `await` on DOM methods yields pending Promises, not values. Wrap mutations in `executeTransaction` with an undo string. Enable Developer Mode (Settings → Plugins) + restart; load/debug via **UXP Developer Tool v2.2.1+**. **STUB.**

## Workarounds
For gaps, keep a CEP/ExtendScript fallback build for <25.6 users; file missing APIs on the Creative Cloud Developer Forums (Adobe prioritizes by request volume). **STUB.**

## Migration
This IS the migration target for `extendscript-core` and `cep`. Tooling: `@adobe/premierepro` (+`@beta`) TS declarations, `@adobe/eslint-plugin-premierepro`, UDT. Distribute as `.ccx` via UPIA / CC Marketplace. **STUB: per-API mapping.**

## Cross-References
- `extendscript-core`
- `cep`
- `cpp-native-sdk`
- `panels`
- `00-technology-status-matrix`

## Sources
- https://developer.adobe.com/premiere-pro/uxp/
- https://developer.adobe.com/premiere-pro/uxp/resources/fundamentals/apis/
- https://github.com/AdobeDocs/uxp-premiere-pro-samples
- https://hyperbrew.co/blog/uxp-plugins-in-premiere-2026/

