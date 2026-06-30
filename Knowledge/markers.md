---
id: markers
title: Markers
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
tags: [markers, sequence-marker, clip-marker, chapter, segmentation, weblink, comment, color]
related: [sequences-tracks-trackitems, captions, xml-fcpxml, uxp]
supersedes: []
superseded_by: [uxp]
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
sources:
  - https://ppro-scripting.docsforadobe.dev/general/marker/
  - https://premiereonscript.com/log-12/
  - https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
---

# Markers

## TL;DR
- Two scopes: `sequence.markers` and `projectItem.getMarkers()`. **STUB.**
- Iterate with `getFirstMarker()`/`getNextMarker(m)`; create with `createMarker(seconds)`; type via `setTypeAsComment/Chapter/Segmentation/WebLink` (return 0 on success).

## Status & Lifecycle
- ExtendScript `legacy/frozen`, EOL 2026-09. UXP markers API is `current`. See `00-technology-status-matrix`.

## Architecture
MarkerCollection on a sequence or project item; Marker objects carry name/comment/start/end/type/color. **STUB.**

## API Surface
`markers.createMarker(timeInSeconds)`; `markers.getFirstMarker()`, `getNextMarker(m)`, `getPrevMarker(m)`, `numMarkers`; `marker.name`, `.comment`, `.start`/`.end` (Time; `.seconds`), `.type`; `marker.getColorByIndex()`/`setColorByIndex(colorIdx, markerIdx)`; `setTypeAsComment()`/`setTypeAsChapter()`/`setTypeAsSegmentation()`/`setTypeAsWebLink()`. **STUB: enum tables.**

## Working Examples
**STUB: read-all, CSV→chapter-markers, export-for-subtitles examples.**

## Limitations
**STUB.**

## Common Errors & Gotchas
Times are Time objects (use `.seconds`). **STUB.**

## Workarounds
**STUB.**

## Migration
**STUB.**

## Cross-References
- `sequences-tracks-trackitems`
- `captions`
- `xml-fcpxml`
- `uxp`

## Sources
- https://ppro-scripting.docsforadobe.dev/general/marker/
- https://premiereonscript.com/log-12/
- https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx

