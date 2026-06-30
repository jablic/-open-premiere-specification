---
id: panels
title: Panels (CEP vs UXP)
category: ui-extensibility
status: mixed
stability: active
doc_status: stub
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [javascript, typescript, html, css]
tags: [panel, cep-panel, uxp-panel, spectrum, ui]
related: [cep, uxp, ai-integration, 00-technology-status-matrix]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://developer.adobe.com/premiere-pro/uxp/
  - https://github.com/Adobe-CEP/CEP-Resources
---

# Panels (CEP vs UXP)

## TL;DR
- Panels come in two flavors: **CEP** (legacy, Chromium, heavy) and **UXP** (current, Spectrum, sandboxed). **STUB.**
- New panels → UXP. Existing panels on <25.6 → CEP, with a UXP build in parallel.

## Status & Lifecycle
- CEP `legacy` (last runtime CEP 12 / Premiere 25.0); UXP `current` (GR 25.6). See `cep`, `uxp`, `00-technology-status-matrix`.

## Architecture
CEP: per-panel CEF process + ExtendScript bridge. UXP: single sandboxed runtime, Spectrum Web Components, manifest-declared permissions. **STUB: comparison matrix.**

## API Surface
Defer to `cep` and `uxp` for concrete APIs. **STUB.**

## Working Examples
**STUB.**

## Limitations
**STUB.**

## Common Errors & Gotchas
**STUB.**

## Workarounds
**STUB.**

## Migration
See `cep` → `uxp`. **STUB.**

## Cross-References
- `cep`
- `uxp`
- `ai-integration`
- `00-technology-status-matrix`

## Sources
- https://developer.adobe.com/premiere-pro/uxp/
- https://github.com/Adobe-CEP/CEP-Resources

