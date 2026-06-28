---
id: sequences-tracks-trackitems
title: Sequences, Tracks, TrackItems, ProjectItems & Bins
category: scripting
status: legacy
stability: frozen
doc_status: complete
introduced: "CC era; New-World scripting ~Premiere 14.1 (2020)"
deprecated: "API work stopped (2024)"
eol: "2026-09"
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript-es3]
tags: [sequence, track, trackitem, projectitem, bin, time, ticks, insertClip, overwriteClip, importMGT, matchName, project-tree, collections]
related: [extendscript-core, essential-graphics-mogrt-text, import, export-rendering-media-encoder, uxp, reverse-engineering-qe-dom, markers]
supersedes: []
superseded_by: [uxp]
sources:
  - https://ppro-scripting.docsforadobe.dev/
  - https://github.com/qmasingarbe/pymiere/blob/master/example_and_documentation.md
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/sequenceeditor
  - https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
confidence: high
last_verified: "2026-06-28"
verified_against_version: "25.x / 26.0"
---

# Sequences, Tracks, TrackItems, ProjectItems & Bins

> The core editing DOM. Everything that touches the timeline or the project panel goes through this
> hierarchy. **Time is measured in ticks (254,016,000,000 / second)**, and since Premiere 14.1
> properties like `start`/`end` require **`Time` objects**, not raw numbers.

## TL;DR
- **Two trees:** the **timeline** (`sequence → tracks → trackItems → components → properties`) and the **project panel** (`rootItem → children` = ProjectItems + bins).
- **Collections are not JS arrays.** Use `.numItems` / `.numTracks` + integer index. No `.forEach`, `.map`, `.length`.
- **Time = ticks.** `TICKS_PER_SECOND = 254016000000`. Convert seconds/frames ↔ ticks explicitly. Pass `Time` objects on 14.1+.
- **Placement:** `insertClip` (ripple) vs `overwriteClip` (replace). MOGRTs via `importMGT` (see `essential-graphics-mogrt-text`).
- **Track targeting is write-only** in the DOM (`setTargeted` exists; there is no reliable getter) — read it back via an FCPXML round-trip.

## Status & Lifecycle
- **Introduced:** grown across CC. **New-World scripting** (~14.1 / 2020) is the watershed: implicit
  numeric→Time coercion was removed, and `start`/`end`/in/out now expect **`Time` objects**.
- **Status:** `legacy/frozen`, EOL **2026-09**.
- **Replacement:** UXP `Project` / `Sequence` / `SequenceEditor` action API (25.0+), async + transactional.
  See `00-technology-status-matrix` for the version authority.

## Architecture

```
app.project
├─ sequences            (SequenceCollection: .numSequences, [i])
│   └─ Sequence
│       ├─ videoTracks  (TrackCollection: .numTracks, [i])
│       │   └─ Track
│       │       ├─ clips        (TrackItemCollection: .numItems, [i])  → TrackItem (video)
│       │       └─ transitions  (TrackItemCollection)
│       ├─ audioTracks  (TrackCollection)
│       │   └─ Track → clips → TrackItem (audio)
│       └─ markers      (MarkerCollection — see markers.md)
│
└─ rootItem            (ProjectItem, the project-panel root)
    └─ children         (ProjectItemCollection: .numItems, [i])
        └─ ProjectItem  (CLIP | BIN | FILE | ROOT)
            └─ children (if BIN) … recursive
```

- A **TrackItem** on the timeline references a **ProjectItem** (`trackItem.projectItem`) in the panel.
- A **TrackItem** is made of **Components** (effects, intrinsics, the MOGRT/text component), each with **ComponentParams** (`properties`). See `essential-graphics-mogrt-text` for the text path.
- The undocumented `qe` tree (after `app.enableQE()`) parallels this with operations the official API lacks (`reverse-engineering-qe-dom`).

## API Surface

### Time / ticks (the unit that trips everyone)
| Fact | Value |
|---|---|
| Ticks per second | `254016000000` (Adobe-confirmed; pymiere `TICKS_PER_SECONDS`) |
| `Time` object | `.ticks` (number-as-string for big values), `.seconds` (get/set) |
| Frames ↔ seconds | `seconds = frames / frameRate`; `frames = round(seconds × frameRate)` |
| Sequence `timebase` | ticks per frame for the sequence |

> **Precision note:** ticks values exceed JS 32-bit int range; the API often exchanges them as strings.
> Compute in seconds/frames and convert at the boundary; avoid integer math that can overflow.

### Sequence (selected members)
| Member | Signature / type | Notes |
|---|---|---|
| `name` | string | r/w |
| `id` / `sequenceID` | string | identity |
| `videoTracks` / `audioTracks` | TrackCollection | `.numTracks`, `[i]` |
| `markers` | MarkerCollection | see `markers` |
| `timebase` | string (ticks/frame) | sequence frame duration |
| `frameSizeHorizontal` / `frameSizeVertical` | number | raster size |
| `getSettings()` / `setSettings(settings)` | SequenceSettings | editing-mode, frame rate, raster, etc. |
| `getPlayerPosition()` / `setPlayerPosition(ticks)` | Time / void | CTI |
| `getInPoint()` / `getOutPoint()` | string (seconds) | work in/out |
| `setInPoint(sec)` / `setOutPoint(sec)` | void | |
| `getZeroPoint()` / `setZeroPoint(ticks)` | string | sequence start offset |
| `insertClip(projectItem, time, vTrackIndex, aTrackIndex)` | void | ripple insert |
| `overwriteClip(projectItem, time, vTrackIndex, aTrackIndex)` | void | overwrite |
| `importMGT(path, ticks, vIdx, aIdx)` | TrackItem | MOGRT (see EGL doc) |
| `importMGTFromLibrary(lib, name, ticks, vIdx, aIdx)` | TrackItem | from CC Library |
| `createSubsequence(ignoreMapping)` | Sequence | subsequence from in/out |
| `exportAsMediaDirect(path, presetPath, workAreaType)` | void | render w/o AME (see export doc) |
| `exportAsFinalCutProXML(path)` | boolean | round-trip channel (see `xml-fcpxml`) |
| `getExportFileExtension(presetPath)` | string | resolve extension |
| `clone()` | void | duplicate sequence |
| `close()` | void | |

### Project-level sequence creation
| Call | Notes |
|---|---|
| `app.project.createNewSequence(name, sequenceID)` | empty sequence (UI-settings dialog may appear depending on version) |
| `app.project.newSequence(...)` / preset-based | preset application is unreliable via documented API; QE `qe.project.newSequence(name, presetPath)` is the practical preset route (undocumented) |
| `app.project.openSequence(sequenceID)` | make a sequence active |
| `app.project.activeSequence` | currently active Sequence (or null) |

### Track (selected)
| Member | Notes |
|---|---|
| `clips` | TrackItemCollection (`.numItems`, `[i]`) |
| `transitions` | TrackItemCollection |
| `id` / `name` / `mediaType` | identity |
| `isMuted()` / `setMute(0\|1)` | mute state |
| `setTargeted(targeted, shouldBroadcast)` | **write-only** targeting (no reliable getter) |
| `insertClip(projectItem, time)` / `overwriteClip(projectItem, time)` | per-track placement |

### TrackItem (selected)
| Member | Notes |
|---|---|
| `name` | clip name |
| `matchName` | internal type id |
| `type` | clip type |
| `mediaType` | "Video" / "Audio" |
| `start` / `end` | **Time** — sequence position (r/w; Time object on 14.1+) |
| `inPoint` / `outPoint` | **Time** — source in/out |
| `duration` | Time |
| `projectItem` | the source ProjectItem |
| `components` | ComponentCollection (effects + intrinsics + MOGRT) |
| `getMGTComponent()` | MOGRT component (see EGL doc) |
| `isSelected()` / `setSelected(sel, broadcast)` | selection |
| `getSpeed()` / `isSpeedReversed()` | speed (set speed is QE-only) |
| `getLinkedItems()` | linked A/V |
| `remove(ripple, alignToVideo)` | delete from timeline |
| `move(time)` | reposition (Time, signed offset) |
| `getColorLabel()` / `setColorLabel(idx)` | label color |

### ProjectItem (selected)
| Member | Notes |
|---|---|
| `name` / `treePath` / `type` | identity (`type`: CLIP=1, BIN=2, ROOT=3, FILE=4 — verify per version) |
| `children` | ProjectItemCollection (bins) |
| `getMarkers()` | MarkerCollection (clip markers) |
| `createBin(name)` / `deleteBin()` / `renameBin(name)` / `moveBin(dest)` | bin ops |
| `createSubClip(name, startTicks, endTicks, hasHardBoundaries, takeVideo, takeAudio)` | subclip |
| `getMediaPath()` / `canChangeMediaPath()` / `changeMediaPath(path, overrideChecks)` | relink |
| `refreshMedia()` | reload from disk |
| `setOffline()` / `attachProxy(path, isHiRes)` | offline/proxy |
| `getColorLabel()` / `setColorLabel(idx)` | label |
| `getProjectMetadata()` / `setProjectMetadata(buffer, fields)` | Premiere metadata |
| `getXMPMetadata()` / `setXMPMetadata(buffer)` | XMP |
| `select()` | select in panel |

### `app.project.rootItem.findItemsMatchingMediaPath(path, ignoreSubclips)`
Returns ProjectItems whose media path matches — the canonical way to locate items after `importFiles`.

## Working Examples

### 1. Ticks / seconds / frames conversion
```js
// ExtendScript (ES3) — Premiere 14.1+
var TICKS_PER_SECOND = 254016000000;
function secondsToTicks(s)        { return Math.round(s * TICKS_PER_SECOND); }
function ticksToSeconds(ticks)    { return Number(ticks) / TICKS_PER_SECOND; }
function framesToSeconds(f, fps)  { return f / fps; }
function secondsToFrames(s, fps)  { return Math.round(s * fps); }

function timeAtSeconds(s) {        // build a Time object the API will accept
    var t = new Time();
    t.seconds = s;
    return t;
}
```

### 2. Insert a bin clip onto the timeline at a given second
```js
// ExtendScript (ES3) — Premiere 14.1+
function insertProjectItemAt(projectItem, atSeconds, vTrackIndex, aTrackIndex) {
    var seq = app.project && app.project.activeSequence;
    if (!seq)         { return { ok: false, err: "No active sequence" }; }
    if (!projectItem) { return { ok: false, err: "No projectItem" }; }
    try {
        var t = timeAtSeconds(atSeconds);            // Time object (Example 1)
        // insertClip ripples; overwriteClip replaces. Indices are 0-based.
        seq.insertClip(projectItem, t, vTrackIndex, aTrackIndex);
        return { ok: true, err: "" };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 3. Find a clip by name on a specific video track
```js
// ExtendScript (ES3)
function findClipOnTrack(seq, vTrackIndex, clipName) {
    if (!seq || !seq.videoTracks || vTrackIndex >= seq.videoTracks.numTracks) { return null; }
    var track = seq.videoTracks[vTrackIndex];
    var clips = track.clips;                          // TrackItemCollection
    for (var i = 0; i < clips.numItems; i++) {        // NOT a JS array
        if (clips[i].name === clipName) { return clips[i]; }
    }
    return null;
}
```

### 4. Walk the entire project tree (bins recursively)
```js
// ExtendScript (ES3) — enumerate every ProjectItem with its bin path
function walkProject(item, path, out) {
    out = out || [];
    path = path || "";
    var kids = item.children;
    if (!kids) { return out; }
    for (var i = 0; i < kids.numItems; i++) {
        var child = kids[i];
        var here = path + "/" + child.name;
        out.push({ name: child.name, type: child.type, treePath: here });
        if (child.children && child.children.numItems > 0) {
            walkProject(child, here, out);            // recurse into bins
        }
    }
    return out;
}
// var all = walkProject(app.project.rootItem, "", []);
```

### 5. Create a new sequence, then make it active
```js
// ExtendScript (ES3)
function newSequenceNamed(name) {
    try {
        // Empty sequence. For preset-driven creation, QE qe.project.newSequence(name, presetPath)
        // is the practical (undocumented) route — see reverse-engineering-qe-dom.
        app.project.createNewSequence(name, name + "-" + (new Date()).getTime());
        return { ok: true, seq: app.project.activeSequence };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### 6. Set a clip's source in/out using Time objects (14.1+ correctness)
```js
// ExtendScript (ES3) — Premiere 14.1+
function trimSource(trackItem, inSeconds, outSeconds) {
    try {
        trackItem.inPoint  = timeAtSeconds(inSeconds);   // raw numbers fail on 14.1+
        trackItem.outPoint = timeAtSeconds(outSeconds);
        return { ok: true };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

## Limitations
- **Track targeting is effectively write-only.** `setTargeted` exists; there is no reliable getter
  for which tracks are targeted. To *read* targeting, export an FCPXML and parse it (`xml-fcpxml`).
- **Preset-based sequence creation** is unreliable through the documented API; the working route is the
  undocumented `qe.project.newSequence(name, presetPath)`.
- **Setting clip speed / reverse** is **not** in the documented API — QE DOM only (`reverse-engineering-qe-dom`).
- **No from-scratch graphic/text creation** — import a MOGRT (`essential-graphics-mogrt-text`).
- **Collections are read-as-indexed only** — you cannot use array iteration helpers.

## Common Errors & Gotchas
- **Symptom:** setting `clip.start`/`end`/`inPoint`/`outPoint` throws or silently no-ops.
  **Cause:** passing a number on Premiere 14.1+. **Fix:** pass a `Time` object (Example 1/6).
- **Symptom:** `clips.forEach is not a function` / `clips.length` is `undefined`.
  **Cause:** treating a collection as a JS array. **Fix:** `for (i=0; i<coll.numItems; i++) coll[i]`.
- **Symptom:** stale/garbage object references after switching sequences or projects.
  **Cause:** holding references across project changes (worse with QE). **Fix:** re-fetch from `app.project` each operation.
- **Symptom:** ticks arithmetic produces wrong/negative values.
  **Cause:** 32-bit overflow on raw ticks. **Fix:** compute in seconds/frames; convert at the edge.
- **Symptom:** `activeSequence` is null mid-script. **Cause:** no sequence open/active. **Fix:** validate first (see `extendscript-core`).
- **Symptom:** `insertClip`/`overwriteClip` lands on the wrong track. **Cause:** index confusion (0-based; video vs audio index args). **Fix:** pass both `vTrackIndex` and `aTrackIndex` deliberately.

## Workarounds
- **Read track targeting / certain UI state:** export FCPXML and parse (`xml-fcpxml`). `confidence: high`.
- **Apply a preset on new sequences:** `qe.project.newSequence(name, presetPath)`. `confidence: medium` (undocumented).
- **Set clip speed / ripple-delete:** QE DOM (`reverse-engineering-qe-dom`). `confidence: low`.

## Migration
Target: UXP `Project` / `Sequence` / **`SequenceEditor`** action API (25.0+), all async + transactional.
- `seq.insertClip(...)` → `SequenceEditor.createInsertProjectItemAction(...)` inside `executeTransaction(cb, undo)`.
- `seq.overwriteClip(...)` → `createOverwriteItemAction(...)`.
- clone a clip → `createCloneTrackItemAction(...)`; delete → `createRemoveItemsAction(...)`.
- `createNewSequence(name, id)` → `createSequenceWithPresetPath(...)` (replaces the deprecated `presetPath` arg).
- Ticks → UXP `TickTime` with `alignToFrame` / `alignToNearestFrame` helpers.
- Remember: UXP DOM methods are **async** — `await` them; properties stay synchronous.

## Cross-References
- `extendscript-core` — runtime, validation, Time/ticks foundation
- `essential-graphics-mogrt-text` — components/properties, MOGRT text on a TrackItem
- `import` — getting media in as ProjectItems; `findItemsMatchingMediaPath`
- `export-rendering-media-encoder` — `exportAsMediaDirect` from a Sequence
- `markers` — the Sequence/ProjectItem marker collections
- `reverse-engineering-qe-dom` — speed, preset-sequence, ripple via QE
- `xml-fcpxml` — FCPXML round-trip to read non-exposed state
- `uxp` — the async/transactional replacement API

## Sources
- Premiere Pro Scripting Guide (Sequence/Track/TrackItem/ProjectItem): https://ppro-scripting.docsforadobe.dev/
- pymiere DOM mirror + ticks constant: https://github.com/qmasingarbe/pymiere/blob/master/example_and_documentation.md
- UXP SequenceEditor action API: https://developer.adobe.com/premiere-pro/uxp/ppro-reference/classes/sequenceeditor
- Adobe-CEP PProPanel sample (.jsx patterns): https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
