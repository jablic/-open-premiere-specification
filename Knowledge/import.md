---
id: import
title: Import
category: workflow
status: legacy
stability: frozen
doc_status: stub
introduced: "CC era"
deprecated: "API frozen 2024"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3]
tags: [import, importFiles, importMGT, projectitem, media-path]
related: [sequences-tracks-trackitems, essential-graphics-mogrt-text, xml-fcpxml, uxp]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/
---

# Import

## TL;DR
- `app.project.importFiles([...], suppressUI, targetBin, asNumberedStills)` is the workhorse. **STUB.**
- `importMGT`/`importMGTFromLibrary` for templates (see `essential-graphics-mogrt-text`).

## Status & Lifecycle
- ExtendScript `legacy/frozen`, EOL 2026-09. UXP `project.importFiles(...)` (async, returns boolean) is `current`.
- See `00-technology-status-matrix`.

## Architecture
Files become ProjectItems under a target bin. **STUB.**

## API Surface
`app.project.importFiles(arrayOfPaths, suppressUI, targetBin, importAsNumberedStills)`. `rootItem.findItemsMatchingMediaPath(path, ignoreSubclips)`. `app.isDocument(path)` validates a project file. **STUB: full args + return.**

## Working Examples
**STUB: add import + locate-imported-item example.**

## Limitations
**STUB.**

## Common Errors & Gotchas
Find imported items afterward via `findItemsMatchingMediaPath` (import returns boolean, not the items). **STUB.**

## Workarounds
**STUB.**

## Migration
UXP `project.importFiles(...)` is async — `await` it. **STUB.**

## Cross-References
- `sequences-tracks-trackitems`
- `essential-graphics-mogrt-text`
- `xml-fcpxml`
- `uxp`

## Sources
- https://ppro-scripting.docsforadobe.dev/

