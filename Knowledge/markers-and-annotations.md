---
id: markers-and-annotations
title: Markers & Timeline Annotations (CEP/UXP/ExtendScript)
category: workflow
status: current
stability: active
doc_status: partial
introduced: "Premiere Pro CC"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript, typescript]
tags: [markers, colors, annotations, timeline, workflow, chapter-markers, cue-points]
related: [sequences-tracks-trackitems, export-rendering-media-encoder, xml-fcpxml, automation]
supersedes: []
superseded_by: []
sources:
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
  - https://ppro-scripting.docsforadobe.dev/general/marker/
  - https://developer.adobe.com/premiere-pro/uxp/ppro_reference/classes/marker/
  - https://github.com/AdobeDocs/uxp-premiere-pro-samples
  - https://helpx.adobe.com/premiere/desktop/organize-media/ingest-proxy-workflow/relink-offline-clips.html
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.x / 26.0"
---

# Markers & Timeline Annotations

> Programmatic creation, modification, and export of timeline markers — the core mechanic for
> marking shots, VFX cues, color grades, and edit points in sequences.

## TL;DR
- **Markers** are timeline annotations with a timecode, text, color, type (standard/chapter/cue-point), and optional metadata.
- **ExtendScript (legacy):** Direct `Marker` object access; synchronous, straightforward DOM.
- **UXP (current, 25.6+):** Async API; markers created via actions (`setMarkerComment`, `setMarkerColor`), not direct instantiation. **Breaking change from CEP/ExtendScript model.**
- **Color system:** Index-based (0–7 standard colors) or hex strings where supported.
- **Use case:** Auto-mark VFX shots, chapter points, sync markers to Premiere from external data (spreadsheet, JSON, MCP server).

## Status & Lifecycle
- **ExtendScript:** `legacy` (supported through Sept 2026), but the most direct API.
- **UXP:** `current` (GR 25.6), async/action-based, still evolving (marker property access improved in 26.0 beta).
- **CEP:** `legacy`; uses ExtendScript bridge (same DOM as ExtendScript panels).

## Architecture

### Marker object hierarchy
```
Sequence
  ├─ videoTracks[n]
  │   └─ trackItems[m]
  │       └─ markers[k]  ← markers on a clip in a track
  └─ markers[j]          ← markers on the sequence timeline itself
```

Markers live at two scopes:
1. **Sequence-level:** `sequence.markers[i]` — affects the entire timeline view
2. **Clip-level:** `trackItem.markers[i]` — attached to a specific clip's playhead (travels with the clip if moved)

### Marker properties

| Property | Type | Read/Write | Notes |
|---|---|---|---|
| `name` | String | RW | Marker comment text (max 256 chars) |
| `start` | Time | RW | In/out point as ticks (Premiere's internal time unit) |
| `duration` | Time | R | Length of marker (if applicable; usually 0) |
| `type` | Integer (0–7) | RW | Marker type/color: 0=red, 1=pink, 2=red-orange, 3=orange, 4=yellow, 5=green, 6=cyan, 7=blue |
| `comments` | String | RW | Extended metadata (differs from `name`; purpose varies by version) |

## API Surface

### ExtendScript — direct access

```javascript
// ExtendScript — Premiere 14.x through 25.x
var seq = app.project.activeSequence;
if (!seq) {
  alert("No active sequence");
} else {
  // Create a marker at timecode 00:01:00:00
  var marker = seq.markers.createMarker(1.0);  // 1.0 seconds
  marker.name = "VFX: Camera shake";
  marker.type = 3;  // orange
  marker.comments = JSON.stringify({ vfx_id: "VFX-0001", priority: "high" });
}
```

**Gotchas:**
- `marker.type` is an integer (0–7), not a string; no enum constants provided.
- Time units: `createMarker(seconds)` expects floating-point seconds, not ticks (despite `start` being in ticks).
- Changes are **immediately visible** in the UI; no explicit "commit" step.

### UXP — actions + async

```javascript
// UXP — Premiere 25.6+
const { application } = require("premierepro");

(async () => {
  const project = await application.activeProject;
  const seq = await project.activeSequence;
  
  if (!seq) {
    console.error("No active sequence");
    return;
  }

  // Markers are created via actions (no direct constructor)
  // Step 1: Create a marker at a specific time
  const markers = await seq.markers;
  const marker = await markers.createMarker(30.0);  // 30 seconds

  // Step 2: Use actions to set properties (async)
  await application.executeAction("setMarkerComment", {
    marker: marker,
    comment: "VFX: Camera shake"
  });

  await application.executeAction("setMarkerColor", {
    marker: marker,
    color: 3  // orange (0–7)
  });

  // Metadata: store as JSON in comment if needed
  const metadata = { vfx_id: "VFX-0001", priority: "high" };
  await application.executeAction("setMarkerComment", {
    marker: marker,
    comment: JSON.stringify(metadata)
  });

  console.log("Marker created at 30.0s");
})();
```

**Key differences from ExtendScript:**
1. All DOM access is **async**; must `await` or chain `.then()`.
2. Marker property setting requires **actions**, not direct property assignment.
3. No synchronous `seq.markers.createMarker(time)` return of marker object; action required.
4. **Performance:** Batch creates benefit from wrapping in `executeTransaction()`.

### Marker types & color index

| Index | Color | Use |
|---|---|---|
| 0 | Red | High priority, errors, reshoots |
| 1 | Pink | Alternative: custom (user-defined) |
| 2 | Red-Orange | Warnings, color grades |
| 3 | Orange | VFX cues, post-production notes |
| 4 | Yellow | Info, general markers |
| 5 | Green | Approved, good takes |
| 6 | Cyan | Sync points, audio alignment |
| 7 | Blue | Cold color, typically unused |

## Working Examples

### Example 1: Batch-create markers from JSON (ExtendScript)

```javascript
// ExtendScript — safe batch marker creation
// Input: sequence, array of {time_sec, text, type_idx, metadata}

function batchCreateMarkers(sequence, markerList) {
  if (!sequence) {
    alert("No sequence provided");
    return;
  }

  var createdCount = 0;
  for (var i = 0; i < markerList.length; i++) {
    var markerSpec = markerList[i];
    try {
      var marker = sequence.markers.createMarker(markerSpec.time_sec);
      marker.name = markerSpec.text || "Marker " + (i + 1);
      marker.type = Math.max(0, Math.min(7, markerSpec.type_idx || 4));  // clamp to 0–7
      
      if (markerSpec.metadata) {
        marker.comments = JSON.stringify(markerSpec.metadata);
      }
      
      createdCount++;
    } catch (e) {
      alert("Error creating marker " + i + ": " + e.toString());
    }
  }
  
  alert("Created " + createdCount + " / " + markerList.length + " markers");
}

// Usage
var seq = app.project.activeSequence;
var markers = [
  { time_sec: 1.5, text: "VFX: Explosion", type_idx: 3, metadata: { type: "explosion" } },
  { time_sec: 5.2, text: "Grade: Color match", type_idx: 2, metadata: { type: "grade" } },
  { time_sec: 12.0, text: "Audio: Sync point", type_idx: 6, metadata: { type: "audio" } }
];

batchCreateMarkers(seq, markers);
```

### Example 2: Read & export markers to CSV (ExtendScript)

```javascript
// ExtendScript — export timeline markers to CSV
function exportMarkersToCSV(sequence, outputPath) {
  if (!sequence || !sequence.markers) {
    alert("Invalid sequence");
    return;
  }

  var csv = "Timecode,Text,Type,Comments\n";
  var markers = sequence.markers;

  for (var i = 0; i < markers.numMarkers; i++) {
    var marker = markers[i];
    var tc = secondsToTimecode(marker.start.seconds);
    var type = ["Red", "Pink", "Red-Orange", "Orange", "Yellow", "Green", "Cyan", "Blue"][marker.type] || "Unknown";
    
    // Escape commas in text/comments
    var text = (marker.name || "").replace(/,/g, ";");
    var comments = (marker.comments || "").replace(/,/g, ";").replace(/\n/g, " ");
    
    csv += tc + "," + text + "," + type + "," + comments + "\n";
  }

  // Write to file
  var file = new File(outputPath);
  file.open("w");
  file.write(csv);
  file.close();

  alert("Markers exported to: " + outputPath);
}

function secondsToTimecode(seconds) {
  var h = Math.floor(seconds / 3600);
  var m = Math.floor((seconds % 3600) / 60);
  var s = Math.floor(seconds % 60);
  var f = Math.floor((seconds % 1) * 24);  // assume 24fps; adjust for your project
  return (h < 10 ? "0" : "") + h + ":" +
         (m < 10 ? "0" : "") + m + ":" +
         (s < 10 ? "0" : "") + s + ":" +
         (f < 10 ? "0" : "") + f;
}

// Usage
var seq = app.project.activeSequence;
exportMarkersToCSV(seq, "/tmp/markers.csv");
```

### Example 3: UXP — read all markers from a sequence (async)

```javascript
// UXP — Premiere 25.6+
const { application } = require("premierepro");

(async () => {
  const project = await application.activeProject;
  const seq = await project.activeSequence;

  if (!seq) {
    console.error("No sequence");
    return;
  }

  const markers = await seq.markers;
  console.log(`Total markers: ${markers.length}`);

  for (let i = 0; i < markers.length; i++) {
    const marker = markers[i];
    const name = await marker.name;
    const startTicks = await marker.start;
    const color = await marker.type;

    console.log(`Marker ${i}: "${name}" @ ticks=${startTicks}, color=${color}`);
  }
})();
```

## Limitations

- **No from-scratch timeline marker type enum.** Hardcoded integers 0–7; no named constants in API.
- **No direct read of marker color name.** Must map index 0–7 to human-readable name manually.
- **UXP marker creation is non-intuitive.** No direct object instantiation; actions required to set properties post-creation.
- **Clip-level markers don't travel with clips when relinking media.** Clip is relinked; marker remains at original sequence timecode.
- **No official marker persistence format.** Markers live in `.prproj` binary; no XMP sidecar or JSON export API. Manual CSV/JSON export required for external backup.

## Common Errors & Gotchas

- **Symptom:** `sequence.markers.createMarker()` returns undefined or error "markers is not defined". **Cause:** Sequence is null or not active. **Fix:** Check `if (seq)` before accessing `.markers`.
- **Symptom:** Marker appears at wrong timecode (off by seconds). **Cause:** Confusing time units: `createMarker(float)` expects **seconds**, not ticks. **Fix:** Convert ticks to seconds: `ticks / sequence.timebase`.
- **Symptom:** (UXP) Marker color doesn't update. **Cause:** Not awaiting the `setMarkerColor` action. **Fix:** Ensure `await application.executeAction(...)`.
- **Symptom:** Marker text truncated or corrupted. **Cause:** Special chars or newlines in marker name. **Fix:** Escape or sanitize: `marker.name = markerSpec.text.replace(/[\n\r]/g, " ")`.

## Workarounds

- **For marker enum:** Define a const map: `const MARKER_COLORS = { RED: 0, ORANGE: 3, GREEN: 5, ... }`.
- **For persistent metadata:** Store as JSON in `marker.comments` or embed in `marker.name` (prefix convention: `[TYPE:VFX-001] Explosion cue`).
- **For clip-level marker tracking:** Store clip GUID + marker timecode in external DB; relink logic must re-associate markers post-relink.

## Migration (ExtendScript → UXP)

| ExtendScript | UXP (25.6+) |
|---|---|
| `seq.markers.createMarker(sec)` → returns marker | Async; marker already created, set properties via actions |
| `marker.name = text` | `executeAction("setMarkerComment", { marker, comment: text })` |
| `marker.type = 3` | `executeAction("setMarkerColor", { marker, color: 3 })` |
| Sync, returns immediately | Async; await required |

## Cross-References
- `sequences-tracks-trackitems` — TrackItem scope; clip-level markers
- `xml-fcpxml` — marker export/import via FCP XML
- `export-rendering-media-encoder` — exporting sequences with markers intact
- `automation` — batch workflows using markers as cue points

## Sources
- https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
- https://ppro-scripting.docsforadobe.dev/general/marker/
- https://developer.adobe.com/premiere-pro/uxp/ppro_reference/classes/marker/
- https://github.com/AdobeDocs/uxp-premiere-pro-samples
