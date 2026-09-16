---
id: automation
title: Automation (pymiere, BridgeTalk, CLI)
category: interop
status: legacy
stability: frozen
doc_status: partial
introduced: null
deprecated: "rides on ExtendScript (EOL 2026-09)"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [python, extendscript, javascript-es3]
tags: [automation, pymiere, bridgetalk, ole, com, applescript, jsx, headless, batch]
related: [extendscript-core, export-rendering-media-encoder, ai-integration, reverse-engineering-qe-dom, cep]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://github.com/qmasingarbe/pymiere
  - https://pypi.org/project/pymiere/
  - https://github.com/qmasingarbe/pymiere/blob/master/demo_ui.py
---

# Automation (pymiere, BridgeTalk, CLI)

## TL;DR
- External drivers for Premiere automation. **Partially seeded.**
- **pymiere** mirrors the ExtendScript DOM in Python over an HTTP/CEP bridge; requires Premiere running (**no headless**). **Unmaintained but functional.**
- Cross-platform glue: Windows OLE/COM, macOS AppleScript/`osascript`, `BridgeTalk` for inter-app.

## Status & Lifecycle
- Rides on ExtendScript → inherits the **2026-09 EOL**. UXP scripting is the forward path. See `00-technology-status-matrix`.

## Architecture
pymiere: Python → HTTP → 'Pymiere Link' CEP extension (node server) → `evalScript` → ExtendScript DOM. Type-hinted Python objects mirror the DOM; `pymiere.objects.qe` exposes QE (+`.inspect()`). **STUB.**

## API Surface
`pymiere.objects.app`, `pymiere.wrappers.*` (e.g. `has_media_encoder()`), `TICKS_PER_SECONDS = 254016000000`. Command-line `.jsx` execution exists but is discouraged (platform-variable). **STUB.**

## Working Examples
```python
# Python (pymiere) — requires Premiere open + Pymiere Link installed
import pymiere
proj = pymiere.objects.app.project
seq = proj.activeSequence
print(seq.name, seq.videoTracks.numTracks)
```
**STUB: import, place-MOGRT, batch-export-via-AME examples.**

## Limitations
No headless mode (Premiere must run). Cannot bind to AME encoder events from Python — do event binding in ExtendScript. README lists testing through PPro 23.1 (2023); newer API surface may be unwrapped. **STUB.**

## Common Errors & Gotchas
Unmaintained — pin your Premiere version. **STUB.**

## Workarounds
For inter-app or generated-`.jsx` flows use `BridgeTalk`/OLE/AppleScript; isolate transport so a UXP port is mechanical later. **STUB.**

## Migration
Move to UXP scripting when the needed API surface lands. **STUB.**

## Cross-References
- `extendscript-core`
- `export-rendering-media-encoder`
- `ai-integration`
- `reverse-engineering-qe-dom`
- `cep`

## Sources
- https://github.com/qmasingarbe/pymiere
- https://pypi.org/project/pymiere/
- https://github.com/qmasingarbe/pymiere/blob/master/demo_ui.py

