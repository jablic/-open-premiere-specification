---
id: premiere-dom-overview
title: Premiere DOM & Scripting API Overview
category: scripting
status: legacy
stability: frozen
doc_status: complete
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

> The authoritative map of Premiere's scriptable object model. Every automation path — ExtendScript,
> CEP bridge, pymiere, or UXP migration — ultimately manipulates these objects. Use this doc as the
> index; deep behavior lives in the per-topic docs linked below.

## TL;DR
- **Single entry point:** `app` (ExtendScript) or `require('premierepro')` (UXP 25.6+).
- **Two parallel trees:** the **project panel** (`rootItem → ProjectItem`) and the **timeline**
  (`sequence → tracks → trackItems → components → properties`).
- **Collections are not JS arrays.** Iterate with `.numItems` / `.numTracks` / `.numMarkers` + integer index `[i]`.
- **Time is ticks-based** (`254016000000` ticks/second). Since Premiere 14.1, `start`/`end`/in/out require **`Time` objects**, not raw numbers.
- **ExtendScript DOM is legacy/frozen** (EOL 2026-09). UXP is the current target but not 1:1 parity.

## Status & Lifecycle
- **ExtendScript reference** (community-hosted, Adobe content): [ppro-scripting.docsforadobe.dev](https://ppro-scripting.docsforadobe.dev/). Banner since Nov 2025: third-party scripting has moved to UXP.
- **UXP reference:** [developer.adobe.com/premiere-pro/uxp/](https://developer.adobe.com/premiere-pro/uxp/) + `ppro-reference` + TypeScript types in `AdobeDocs/uxp-premiere-pro`.
- **QE DOM:** undocumented parallel tree after `app.enableQE()` — see `reverse-engineering-qe-dom`.
- Status/version authority: `00-technology-status-matrix`.

## Architecture

### Object tree under `app`

```
app  (Application)
├── version, build, userName, getAppSystemCompatibilityReport()
├── project          → Project (null if no project open)
├── encoder          → Encoder (AME queue interface)
├── enableQE()       → qe (undocumented QE DOM — separate tree)
├── getProjectViewIDs() / getProjectFromViewID(id) / getProjectViewSelection(viewID)
├── setSDKEventMessage(key, value, global)   // C++ SDK bridge
├── setExtensionPersistent(extId, 0|1)      // keep CEP panel loaded
└── isDocumentOpen() / isDocumentDirty() / anyDocumentOpen()

app.project  (Project)
├── name, path
├── activeSequence   → Sequence | null
├── rootItem         → ProjectItem (ROOT — project panel root)
├── sequences        → SequenceCollection (.numSequences, [i])
├── importFiles(...), importAllAEComps(...), save(), closeDocument()
├── createNewSequence(name, id), openSequence(id), deleteSequence(seq)
├── getInsertionBin() / setInsertionBin(bin)
├── exportFinalCutProXML(path), exportOMF(...), exportAAF(...)
├── getProjectPanelMetadata() / setProjectPanelMetadata(...)
└── production / projectManager (Production workflows — see below)

Project.rootItem  (ProjectItem, type ROOT)
└── children       → ProjectItemCollection (.numItems, [i])
    └── ProjectItem (CLIP | BIN | FILE | ROOT)
        ├── children (if BIN) … recursive
        ├── getMediaPath(), changeMediaPath(), refreshMedia()
        ├── getMarkers() → MarkerCollection
        └── getProjectMetadata() / getXMPMetadata()

Sequence  (timeline)
├── name, id / sequenceID, timebase
├── videoTracks    → TrackCollection (.numTracks, [i])
├── audioTracks    → TrackCollection
├── markers        → MarkerCollection (.numMarkers, linked list API)
├── getSettings() / setSettings()
├── getPlayerPosition() / setPlayerPosition(ticks)
├── getInPoint() / getOutPoint() / setInPoint() / setOutPoint()
├── insertClip(projectItem, time, vIdx, aIdx)
├── overwriteClip(projectItem, time, vIdx, aIdx)
├── importMGT(path, ticks, vIdx, aIdx) → TrackItem
├── createCaptionTrack(projectItem, startTime, format)
├── exportAsMediaDirect(path, preset, workAreaType)
├── exportAsFinalCutProXML(path)
└── clone() / close()

Track  (video or audio)
├── clips          → TrackItemCollection (.numItems, [i])
├── transitions    → TrackItemCollection
├── id, name, mediaType
├── isMuted() / setMute(0|1)
├── setTargeted(targeted, broadcast)   // write-only — no reliable getter
└── insertClip() / overwriteClip()

TrackItem  (timeline clip instance)
├── name, matchName, type, mediaType
├── start, end, inPoint, outPoint, duration  → Time objects (14.1+)
├── projectItem    → ProjectItem (source reference — NOT owned by sequence)
├── components     → ComponentCollection (.numItems, [i])
├── getMGTComponent() → Component
├── isSelected() / setSelected()
├── getSpeed() / isSpeedReversed()   // set speed = QE only
├── getLinkedItems()
├── remove(ripple, alignToVideo) / move(time)
└── getColorLabel() / setColorLabel()

Component  (effect, intrinsic, or MOGRT module)
├── matchName, displayName
└── properties     → ComponentParamCollection (.numItems, [i])
    └── ComponentParam
        ├── displayName, matchName
        ├── getValue() / setValue(value, updateUI)
        └── areKeyframesSupported() / addKey() / … (version-dependent)

Marker  (sequence or clip scope)
├── name, comment, type
├── start, end     → Time (read); createMarker(time) takes seconds (float)
└── setTypeAsComment/Chapter/Segmentation/WebLink()

Time
├── ticks (string or number — exceeds 32-bit int)
└── seconds (get/set)

app.encoder  (Encoder)
├── encodeSequence / encodeFile / encodeProjectItem → job-ID string
├── launchEncoder(), startBatch()
├── bind(eventName, handler)   // onEncoderJobQueued, Complete, Error, Progress
└── ENCODE_ENTIRE / ENCODE_IN_TO_OUT / ENCODE_WORK_AREA constants
```

### Per-object responsibility

| Object | Scope | Owns / references | Does NOT own |
|---|---|---|---|
| **Application** | Host runtime | Current `project`, `encoder` | Media files on disk |
| **Project** | Open `.prproj` | `rootItem`, `sequences[]`, insertion bin | Source media files |
| **ProjectItem** | Project panel node | Media path reference, clip markers, bin children | Timeline edit decisions |
| **Sequence** | One timeline | Tracks, sequence markers, edit structure | Source media files |
| **Track** | One lane (V/A) | TrackItems on that lane | Clips on other tracks |
| **TrackItem** | One timeline instance | Components (effects/MOGRT), in/out on timeline | The underlying media file |
| **Component** | Effect or MOGRT module | ComponentParams (properties) | Other components |
| **ComponentParam** | One editable property | Current value (often JSON string for text) | — |
| **Marker** | Annotation point/span | Name, comment, type, color | — |
| **Encoder** | AME queue bridge | Job IDs (strings) | Rendered output files until AME completes |
| **Time** | Temporal value | Ticks/seconds representation | — |

> **Critical distinction:** a **TrackItem** is a timeline *instance*; its **ProjectItem** is the project-panel
> *reference*. Many TrackItems can point at one ProjectItem. Relink and path changes happen on **ProjectItem**,
> not TrackItem. See `best-practices`.

### Collection access pattern

Premiere collections are **host-native indexed lists**, not JavaScript arrays.

| Collection type | Count property | Index access | Linked-list variant |
|---|---|---|---|
| `ProjectItemCollection` | `.numItems` | `[i]` (0-based) | — |
| `TrackItemCollection` | `.numItems` | `[i]` | — |
| `ComponentCollection` / `ComponentParamCollection` | `.numItems` | `[i]` | — |
| `TrackCollection` | `.numTracks` | `[i]` | — |
| `SequenceCollection` | `.numSequences` | `[i]` | — |
| `MarkerCollection` | `.numMarkers` | — | `getFirstMarker()` → `getNextMarker(m)` |

```js
// ExtendScript (ES3) — correct collection iteration
var clips = track.clips;
for (var i = 0; i < clips.numItems; i++) {
    var item = clips[i];           // NOT clips.get(i), NOT clips.forEach
    // ...
}

// WRONG — these do not exist on Premiere collections:
// clips.length, clips.forEach(), clips.map(), Array.isArray(clips)
```

## API Surface

### Application (`app`)

| Member | Type | Notes |
|---|---|---|
| `version` | string | e.g. `"25.3.0"` — parse major for version gates |
| `build` | string | Build string |
| `project` | Project \| null | Currently open project |
| `encoder` | Encoder | AME queue interface |
| `enableQE()` | void → enables `qe` | Undocumented QE DOM — last resort |
| `getAppSystemCompatibilityReport()` | string | Diagnostics |
| `isDocumentOpen()` / `isDocumentDirty()` | boolean | |
| `anyDocumentOpen()` | boolean | Any project open |
| `setExtensionPersistent(id, 0\|1)` | void | Keep CEP panel loaded across focus changes |
| `getProjectViewIDs()` | number[] | Multi-project view IDs |
| `getProjectFromViewID(id)` | Project | |
| `getProjectViewSelection(viewID)` | ProjectItem[] | Panel selection |

### Project

| Member | Type | Notes |
|---|---|---|
| `name` / `path` | string | |
| `activeSequence` | Sequence \| null | Currently active timeline |
| `rootItem` | ProjectItem | Project panel root (type ROOT) |
| `sequences` | SequenceCollection | All sequences in project |
| `importFiles(paths, suppressUI, targetBin, importAsNumberedStills)` | boolean | Returns success |
| `importAllAEComps(path, suppressUI, targetBin)` | boolean | Import AE project comps |
| `createNewSequence(name, sequenceID)` | void | Empty sequence |
| `openSequence(sequenceID)` | boolean | Activate a sequence |
| `deleteSequence(sequence)` | void | |
| `save()` / `closeDocument(save)` | void | |
| `getInsertionBin()` / `setInsertionBin(bin)` | ProjectItem | Default import target |
| `exportFinalCutProXML(path)` | boolean | Whole-project FCP7 XML |
| `exportAAF(...)` / `exportOMF(...)` | boolean | Interchange |
| `production` | Production | Team Projects (version-dependent) |
| `projectManager` | ProjectManager | Consolidate/transfer |

### Sequence

See `sequences-tracks-trackitems` for the full member table. Key groups:
- **Structure:** `videoTracks`, `audioTracks`, `markers`, `timebase`
- **Transport:** `getPlayerPosition`, `setPlayerPosition`, in/out points
- **Editing:** `insertClip`, `overwriteClip`, `importMGT`, `createCaptionTrack`
- **Export:** `exportAsMediaDirect`, `exportAsFinalCutProXML`, `getExportFileExtension`
- **Lifecycle:** `clone`, `close`, `createSubsequence`

### Track / TrackItem / ProjectItem

Full tables in `sequences-tracks-trackitems`. Remember:
- **Track** holds `clips` and `transitions` collections.
- **TrackItem** bridges timeline ↔ `projectItem` ↔ `components`.
- **ProjectItem** is the project-database node; bins recurse via `children`.

### Component / ComponentParam

| Component member | Notes |
|---|---|
| `matchName` | Internal effect ID (e.g. `"AE.ADBE Text"`) |
| `displayName` | UI label |
| `properties` | ComponentParamCollection |

| ComponentParam member | Notes |
|---|---|
| `displayName` / `matchName` | Lookup keys |
| `getValue()` | Returns string (MOGRT Source Text = JSON string) |
| `setValue(value, updateUI)` | Pass `updateUI = true` to refresh panels |
| `getParamForDisplayName(name)` | On `properties` collection — preferred lookup |
| Keyframe methods | Version/build-dependent; test on target |

### Marker

| MarkerCollection | Notes |
|---|---|
| `numMarkers` | Count |
| `createMarker(timeSeconds)` | Time as **float seconds** (not Time object) |
| `getFirstMarker()` / `getNextMarker(m)` / `getPrevMarker(m)` | Linked-list walk |
| `deleteMarker(m)` / `moveMarker(m, newTimeSeconds)` | |

| Marker | Notes |
|---|---|
| `name`, `comment` | r/w strings |
| `start`, `end` | **Time** objects — read via `.seconds` |
| `type` | `"Comment"`, `"Chapter"`, etc. |
| `setTypeAsComment()` etc. | Return `0` on success |
| `setColorByIndex(idx)` / `getColorByIndex()` | Palette 0–7 |

See `markers` for color index table and UXP equivalents.

### Encoder

| Member | Notes |
|---|---|
| `encodeSequence(seq, outPath, eprPath, workArea, removeOnComplete)` | Returns job-ID string; `"0"` on failure |
| `encodeFile(...)` / `encodeProjectItem(...)` | Same pattern |
| `launchEncoder()` | Start AME if needed |
| `startBatch()` | Process queue |
| `bind(event, fn)` | Async completion hooks |
| `ENCODE_ENTIRE` / `ENCODE_IN_TO_OUT` / `ENCODE_WORK_AREA` | Work-area constants |

**HEVC/H.265 blocked since Premiere 25.5** — returns a job ID but queues nothing. See `export-rendering-media-encoder`.

### Time

| Fact | Value |
|---|---|
| Ticks per second | `254016000000` |
| Constructor | `new Time()` then set `.seconds` or `.ticks` |
| 14.1+ rule | Pass `Time` objects to `start`/`end`/`inPoint`/`outPoint` — raw numbers fail |
| Precision | Ticks exceed 32-bit int; API often uses strings — compute in seconds/frames at boundaries |

```js
// ExtendScript (ES3) — Premiere 14.1+
var TICKS_PER_SECOND = 254016000000;
function timeAtSeconds(s) {
    var t = new Time();
    t.seconds = s;
    return t;
}
function secondsToTicks(s) { return Math.round(s * TICKS_PER_SECOND); }
```

## Working Examples

### Walk the whole project (bins + sequences + active timeline)

```js
// ExtendScript (ES3) — Premiere 14.x+
//@include "json2.js"

function walkProjectItems(item, path, out) {
    out = out || [];
    path = path || "";
    var kids = item.children;
    if (!kids) { return out; }
    for (var i = 0; i < kids.numItems; i++) {
        var child = kids[i];
        var here = path + "/" + child.name;
        out.push({
            name: child.name,
            type: child.type,       // CLIP=1, BIN=2, ROOT=3, FILE=4 (verify per version)
            treePath: here,
            mediaPath: (child.getMediaPath ? child.getMediaPath() : "")
        });
        if (child.children && child.children.numItems > 0) {
            walkProjectItems(child, here, out);
        }
    }
    return out;
}

function describeOpenProject() {
    if (!app.project) { return JSON.stringify({ ok: false, err: "No project open" }); }
    var proj = app.project;
    var seq = proj.activeSequence;
    var summary = {
        ok: true,
        projectName: proj.name,
        projectPath: proj.path,
        sequenceCount: proj.sequences.numSequences,
        activeSequence: seq ? {
            name: seq.name,
            videoTracks: seq.videoTracks.numTracks,
            audioTracks: seq.audioTracks.numTracks,
            markers: seq.markers.numMarkers
        } : null,
        projectItems: walkProjectItems(proj.rootItem, "", [])
    };
    return JSON.stringify(summary);
}

$.writeln(describeOpenProject());
```

### Resolve a component parameter by display name

```js
// ExtendScript (ES3) — generic ComponentParam lookup
function findParam(trackItem, displayName) {
    if (!trackItem || !trackItem.components) { return null; }
    var comps = trackItem.components;
    for (var i = 0; i < comps.numItems; i++) {
        var comp = comps[i];
        var props = comp.properties;
        if (props.getParamForDisplayName) {
            var p = props.getParamForDisplayName(displayName);
            if (p) { return { component: comp, param: p }; }
        }
        for (var j = 0; j < props.numItems; j++) {
            if (props[j].displayName === displayName) {
                return { component: comp, param: props[j] };
            }
        }
    }
    return null;
}
```

## Limitations

Hard walls for the documented ExtendScript DOM (frozen — will not be fixed):

| Limitation | Detail |
|---|---|
| **Frozen API** | No new members since 2024; gaps are permanent for ExtendScript |
| **No from-scratch text/graphics** | Must import a `.mogrt`; no title/EGL creation API |
| **Track targeting is write-only** | `setTargeted` exists; no reliable getter — use FCPXML round-trip |
| **Clip speed / reverse** | Not in documented API — QE DOM only |
| **Preset-based sequence creation** | Unreliable via documented API — QE `newSequence(name, presetPath)` |
| **Effect application by display name** | Not in documented API — QE DOM only |
| **Caption text read/write** | Severely limited; caption blocks are serialized data |
| **HEVC programmatic export** | Blocked since 25.5 by design |
| **Synchronous / UI-blocking** | Long loops freeze Premiere — chunk work or use external driver |
| **Collections ≠ arrays** | No `.length`, `.forEach`, spread, or `Array.isArray` |
| **Stale object references** | Re-fetch from `app.project` after project/sequence switches |
| **Multi-project** | `getProjectViewIDs` exists but most scripts assume single open project |
| **Production / Team Projects** | Partial surface; test on target build |
| **Renderer / GPU settings** | Not meaningfully script-controllable |
| **Auto-transcription (Speech to Text)** | Host feature, not a stable scripting API |
| **Upgrade captions to graphics** | UI-only workflow |

## Common Errors & Gotchas

- **Symptom:** `clips.forEach is not a function`. **Cause:** treating a collection as a JS array. **Fix:** `for (i=0; i<coll.numItems; i++) coll[i]`.
- **Symptom:** `clip.start = 5` throws or no-ops. **Cause:** raw number on 14.1+. **Fix:** `clip.start = timeAtSeconds(5)`.
- **Symptom:** `[object Object]` in concatenated strings. **Cause:** New-World scripting removed implicit coercion. **Fix:** `String(x)`.
- **Symptom:** MOGRT text updates on wrong clip. **Cause:** editing ProjectItem instead of TrackItem (or vice versa). **Fix:** see `best-practices`.
- **Symptom:** ticks math produces garbage. **Cause:** 32-bit overflow. **Fix:** compute in seconds; convert at boundary.
- **Symptom:** `activeSequence` is null mid-script. **Cause:** no sequence active. **Fix:** validate chain before every operation.
- **Symptom:** `EvalScript error.` from CEP with no detail. **Cause:** uncaught host exception. **Fix:** wrap in try/catch; return JSON envelope (`extendscript-core`).

## Workarounds

| Need | Workaround | Confidence |
|---|---|---|
| Read track targeting | Export FCPXML, parse (`xml-fcpxml`) | high |
| Apply effect by name / set speed / ripple | QE DOM after `app.enableQE()` | low |
| Preset-driven new sequence | `qe.project.newSequence(name, presetPath)` | medium |
| MOGRT text (UXP gap) | Stay on ExtendScript/CEP until UXP parity | high |
| Async-like batch edits | Chunk + `$.sleep`; drive from CEP/UXP side | medium |
| Read non-exposed UI state | FCP7 XML export round-trip | high |

## Migration — ExtendScript → UXP mapping

Target: `const ppro = require('premierepro')` (Premiere **25.6+**). DOM methods are **async** (`await`);
property get/set remain **sync**. Mutations require `executeTransaction(cb, undoString)`.

| ExtendScript (`app`) | UXP (`premierepro`) | Notes |
|---|---|---|
| `app.project` | `await Project.getActiveProject()` | Returns Project or null |
| `project.activeSequence` | `await project.getActiveSequence()` | Async getter |
| `project.rootItem` | `project.rootItem` | Sync property |
| `project.sequences[i]` | `await project.getSequences()` | Returns array |
| `project.importFiles(...)` | `await project.importFiles(...)` | Async |
| `project.createNewSequence(name, id)` | `await project.createSequenceWithPresetPath(...)` | Preset path replaces deprecated arg |
| `sequence.insertClip(...)` | `SequenceEditor.createInsertProjectItemAction(...)` | Inside `executeTransaction` |
| `sequence.overwriteClip(...)` | `createOverwriteItemAction(...)` | Inside transaction |
| `trackItem.remove(...)` | `createRemoveItemsAction(...)` | Inside transaction |
| TrackItem clone | `createCloneTrackItemAction(...)` | Inside transaction |
| `sequence.exportAsFinalCutProXML(path)` | `await sequence.exportAsFinalCutProXML(path)` | Async |
| `app.encoder.encodeSequence(...)` | UXP Encoder + `Preset` API | Verify parity on build |
| `new Time(); t.seconds = n` | `TickTime.createWithSeconds(n)` | + `alignToFrame` helpers |
| `component.properties[j].getValue()` | Component property getters | MOGRT text blob: **no UXP parity yet** |
| `sequence.markers.createMarker(t)` | Marker APIs on Sequence/ProjectItem | Async in UXP |
| `app.enableQE()` / `qe.*` | No equivalent | QE has no UXP path |
| `CSInterface.evalScript(...)` | Direct in-runtime calls | No bridge needed |
| json2.js polyfill | Native `JSON` | UXP is modern JS |

**Known UXP gaps (25.6):** MOGRT Source Text JSON manipulation, some QE-only ops, early missing
sequence-frame-rate getter, incomplete Spectrum Web Components support. File gaps on Adobe Developer Forums.

## Cross-References
- `extendscript-core` — runtime, ES3 rules, json2, UTF-8, CEP bridge
- `sequences-tracks-trackitems` — Time/ticks, placement, project tree
- `essential-graphics-mogrt-text` — ComponentParam / Source Text JSON
- `markers` — MarkerCollection linked-list API
- `export-rendering-media-encoder` — Encoder / AME pipeline
- `captions` — caption tracks (separate from video tracks)
- `uxp` — async/transactional replacement
- `reverse-engineering-qe-dom` — parallel undocumented tree
- `best-practices` — validation chain, PKC agent rules
- `00-technology-status-matrix` — lifecycle authority

## Sources
- Premiere Pro Scripting Guide: https://ppro-scripting.docsforadobe.dev/
- UXP Premiere Pro reference: https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
- pymiere DOM mirror (ticks constant): https://github.com/qmasingarbe/pymiere
