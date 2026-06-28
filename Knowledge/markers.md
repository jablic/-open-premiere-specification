---
id: markers
title: Markers
category: workflow
status: legacy
stability: frozen
doc_status: complete
introduced: "CC era"
deprecated: "API frozen 2024"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3, javascript]
tags: [markers, sequence-marker, clip-marker, chapter, segmentation, weblink, comment, color, marker-type]
related: [sequences-tracks-trackitems, captions, xml-fcpxml, uxp]
supersedes: []
superseded_by: [uxp]
sources:
  - https://ppro-scripting.docsforadobe.dev/general/marker/
  - https://premiereonscript.com/log-12/
  - https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Markers

> Timeline and clip markers for chapters, comments, web links, and segmentation.
> Two scopes: **sequence markers** (`sequence.markers`) and **clip markers** (`projectItem.getMarkers()`).

## TL;DR
- Iterate: `getFirstMarker()` → `getNextMarker(m)` until `null`.
- Create: `markers.createMarker(timeInSeconds)` — time is a **number** (seconds), not a `Time` object for create.
- Read times: `marker.start` / `marker.end` are **`Time` objects** — use `.seconds`.
- Set type: `setTypeAsComment()` / `setTypeAsChapter()` / `setTypeAsSegmentation()` / `setTypeAsWebLink()` — return `0` on success.
- Export to subtitles: markers with type Chapter can drive caption workflows (UI-heavy; see `captions`).

## Status & Lifecycle
- ExtendScript markers API is **legacy/frozen**, EOL **2026-09**.
- UXP exposes marker APIs on Sequence/ProjectItem (async) — `current` for 25.6+.
- Markers also appear in **FCP7 XML exports** as `<marker>` elements (`xml-fcpxml`).

## Architecture
```
Sequence
  └─ markers (MarkerCollection)
       └─ Marker { name, comment, start, end, type, guides }
ProjectItem (source clip)
  └─ getMarkers() → MarkerCollection
```

Sequence markers are timeline-global. Clip markers travel with the source `ProjectItem` and appear on every instance.

## API Surface

### MarkerCollection

| Member | Type | Notes |
|---|---|---|
| `numMarkers` | `number` | Count |
| `createMarker(time)` | `Marker` | `time` in **seconds** (float) |
| `createMarker(time, duration)` | `Marker` | Span marker (if supported) |
| `getFirstMarker()` | `Marker` or `null` | |
| `getNextMarker(marker)` | `Marker` or `null` | |
| `getPrevMarker(marker)` | `Marker` or `null` | |
| `deleteMarker(marker)` | — | |
| `moveMarker(marker, newTime)` | — | `newTime` in seconds |

### Marker object

| Member | Type | Notes |
|---|---|---|
| `name` | `string` | |
| `comment` | `string` | |
| `start` | `Time` | Use `.seconds` |
| `end` | `Time` | Use `.seconds`; point markers: start ≈ end |
| `type` | `string` | `"Comment"`, `"Chapter"`, etc. |
| `getColorByIndex()` | `number` | Palette index |
| `setColorByIndex(idx, markerIdx)` | `number` | Returns 0 on success |
| `setTypeAsComment()` | `number` | 0 = success |
| `setTypeAsChapter()` | `number` | |
| `setTypeAsSegmentation()` | `number` | |
| `setTypeAsWebLink()` | `number` | |
| `setGuid(num, guidString)` | — | Web link target |
| `getWebLinkURL()` | `string` | |

### Marker color indices (common)

| Index | Color |
|---|---|
| 0 | Green |
| 1 | Red |
| 2 | Purple |
| 3 | Orange |
| 4 | Yellow |
| 5 | White |
| 6 | Blue |
| 7 | Cyan |

## Working Examples

```js
// ExtendScript (ES3) — read all sequence markers
function getSequenceMarkers(seq) {
  var out = [];
  var m = seq.markers.getFirstMarker();
  while (m) {
    out.push({
      name: m.name,
      comment: m.comment,
      start: m.start.seconds,
      end: m.end.seconds,
      type: m.type
    });
    m = seq.markers.getNextMarker(m);
  }
  return out;
}
```

```js
// ExtendScript (ES3) — CSV chapter markers → sequence markers
function importChapterMarkers(csvLines, seq) {
  // csvLines: ["00:01:00:00,Intro", "00:02:30:00,Section 2", ...]
  var fps = seq.timebase; // sequence frame rate
  for (var i = 0; i < csvLines.length; i++) {
    var parts = csvLines[i].split(',');
    var tc = parts[0];
    var label = parts.slice(1).join(',');
    var secs = timecodeToSeconds(tc, fps);
    var marker = seq.markers.createMarker(secs);
    marker.name = label;
    marker.setTypeAsChapter();
  }
}
```

```js
// ExtendScript (ES3) — add comment marker at playhead
function markerAtPlayhead(seq, label) {
  var t = seq.getPlayerPosition().seconds;
  var m = seq.markers.createMarker(t);
  m.name = label;
  m.setTypeAsComment();
  return m;
}
```

## Limitations
- No bulk import API — loop `createMarker` manually.
- Marker → caption conversion is **UI-driven** ("Create captions from markers") — not fully scriptable.
- Web link markers require GUID setup for some targets.
- UXP marker API surface may differ — verify against `@adobe/premierepro` types for 25.6+.

## Common Errors & Gotchas
- **Symptom:** Wrong marker position. **Cause:** Passed `Time` object to `createMarker` instead of seconds. **Fix:** Use `time.seconds` float.
- **Symptom:** `setTypeAsChapter()` returns non-zero. **Cause:** Invalid marker state or read-only marker. **Fix:** Create fresh marker; check return code.
- **Symptom:** Clip markers missing on duplicate clips. **Cause:** Clip markers live on **source ProjectItem**, not TrackItem. **Fix:** `projectItem.getMarkers()` on the master clip.
- **Symptom:** Exported XML markers don't match sequence. **Cause:** Frame vs seconds in XML (`<in>` is frames). **Fix:** Convert via sequence timebase (`xml-fcpxml`).

## Workarounds
- Export FCP7 XML and parse `<marker>` tags for external pipelines (`xml-fcpxml`, `Examples/python/parse_premiere_fcpxml.py`).
- For VFX pull lists, combine markers + metadata (`automation`, PKC recipe REC-0003 pattern).

## Migration

| ExtendScript | UXP (25.6+) |
|---|---|
| `sequence.markers.createMarker(secs)` | Async marker APIs on Sequence — `await` |
| Sync iteration | Check `ppro.Marker` / `MarkerCollection` in UXP reference |
| `projectItem.getMarkers()` | UXP equivalent on ProjectItem |

## Cross-References
- `sequences-tracks-trackitems` — sequence timebase, `getPlayerPosition`
- `captions` — marker-to-caption workflow
- `xml-fcpxml` — marker export in FCP7 XML
- `uxp` — current marker API

## Sources
- https://ppro-scripting.docsforadobe.dev/general/marker/
- https://premiereonscript.com/log-12/
- https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
