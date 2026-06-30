---
id: debugging
title: Debugging & Tooling
category: meta
status: mixed
stability: active
doc_status: stub
introduced: null
deprecated: null
eol: null
min_premiere_version: null
api_namespace: none
languages: [extendscript, javascript, typescript]
tags: [debugging, extendscript-debugger, vscode, devtools, udt, writeln, breakpoints, types-for-adobe]
related: [extendscript-core, cep, uxp, automation]
supersedes: []
superseded_by: []
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://blog.developer.adobe.com/en/publish/2019/06/debugging-your-adobe-panel
  - https://github.com/Adobe-CEP/Getting-Started-guides/blob/master/Client-side%20Debugging/readme.md
  - https://github.com/aenhancers/Types-for-Adobe
---

# Debugging & Tooling

## TL;DR
- Three debug paths by runtime: **ExtendScript** → VS Code ExtendScript Debugger + `$.writeln`; **CEP** → Chrome DevTools via `.debug`/`PlayerDebugMode`; **UXP** → UDT Chromium DevTools. **STUB.**

## Status & Lifecycle
- Tooling spans all statuses. ESTK is deprecated (use VS Code). See `00-technology-status-matrix`.

## Architecture
Each runtime has its own inspector. **STUB.**

## API Surface
ExtendScript: `$.writeln`, `$.write`, `alert`, breakpoints via `Adobe.extendscript-debug`. CEP: see `cep` (PlayerDebugMode + `.debug` + localhost port). UXP: load/inspect via UXP Developer Tool v2.2.1+. **STUB.**

## Working Examples
**STUB.**

## Limitations
ExtendScript Debugger is best for self-contained scripts; can be flaky inside complex panels. **STUB.**

## Common Errors & Gotchas
Modern Chrome console may break on removed `KeyboardEvent.keyIdentifier` for CEP — use `chrome://inspect` or older Chrome. **STUB.**

## Workarounds
**Types-for-Adobe** for IntelliSense as a 'documentation' substitute given incomplete official docs. **STUB.**

## Migration
**STUB.**

## Cross-References
- `extendscript-core`
- `cep`
- `uxp`
- `automation`

## Sources
- https://blog.developer.adobe.com/en/publish/2019/06/debugging-your-adobe-panel
- https://github.com/Adobe-CEP/Getting-Started-guides/blob/master/Client-side%20Debugging/readme.md
- https://github.com/aenhancers/Types-for-Adobe

