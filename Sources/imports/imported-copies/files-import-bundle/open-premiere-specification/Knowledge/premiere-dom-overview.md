---
id: premiere-dom-overview
title: Premiere DOM & Scripting API Overview
category: scripting
status: legacy
stability: frozen
doc_status: partial
introduced: "CC era"
deprecated: "API frozen 2024"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3]
tags: [dom, api-map, app, project, reference]
related: [extendscript-core, sequences-tracks-trackitems, uxp, reverse-engineering-qe-dom]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
---

# Premiere DOM & Scripting API Overview

## TL;DR
- Map of the scriptable object model: where every object lives under `app`.
- ExtendScript DOM is `legacy/frozen`; the UXP `premierepro` module is the `current` equivalent.
- Use this as the index; deep detail lives in the per-object docs.

## Status & Lifecycle
- **ExtendScript reference** (community-hosted, Adobe content): `ppro-scripting.docsforadobe.dev`. Banner since Nov 2025: 3rd-party scripting has moved to UXP.
- **UXP reference:** `developer.adobe.com/premiere-pro/uxp/` (+ `ppro-reference`, types in `AdobeDocs/uxp-premiere-pro` `types.d.ts`).
- Status/version authority: see `00-technology-status-matrix`.

## Architecture
Top of tree: `app` → `project` → `sequences[]`/`rootItem` → tracks → trackItems → components → properties. Parallel undocumented tree: `qe` after `app.enableQE()`. **STUB: insert full object-tree diagram + per-object responsibility table.**

## API Surface
Core objects: `Application` (`app.version`, `app.build`, `app.encoder`, `app.project`, `app.enableQE`), `Project`, `Sequence`, `Track`, `TrackItem`, `ProjectItem`, `Component`, `ComponentParam`, `Marker`, `Encoder`, `Metadata`, `Production`, `ProjectManager`, `Time`, and the `*Collection` wrappers (`.numItems`/index access). **STUB: enumerate members per object with signatures.**

## Working Examples
See `extendscript-core` for the entry-point and validation patterns. **STUB: add a 'walk the whole project' reference script.**

## Limitations
Frozen API; gaps are permanent for ExtendScript. Track targeting is not queryable. **STUB: complete list.**

## Common Errors & Gotchas
Collections use `.numItems` + integer indexing (not JS array methods). New-World scripting requires `Time` objects and explicit `String()` coercion. **STUB: expand.**

## Workarounds
**STUB.**

## Migration
ExtendScript `app` (sync) → UXP `require('premierepro')` (async methods). **STUB: object-by-object mapping table.**

## Cross-References
- `extendscript-core`
- `sequences-tracks-trackitems`
- `uxp`
- `reverse-engineering-qe-dom`
- `00-technology-status-matrix`

## Sources
- https://ppro-scripting.docsforadobe.dev/
- https://developer.adobe.com/premiere-pro/uxp/ppro-reference/

