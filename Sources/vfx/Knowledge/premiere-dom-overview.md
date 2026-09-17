---
id: premiere-dom-overview
title: Premiere Pro DOM Overview
category: reference
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app
languages: [extendscript, uxp]
tags: [dom, reference, object-model, api-hierarchy]
related: [extendscript-core, sequences-tracks-trackitems, uxp]
sources: [
  "https://ppro-scripting.docsforadobe.dev/",
  "Adobe Premiere Pro Scripting Reference",
  "Production testing: Premiere 25.x"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Premiere Pro DOM Overview

## TL;DR

**Premiere DOM = object hierarchy accessible via ExtendScript and UXP.** Root: `app` (Premiere application). Primary objects: `Project`, `Sequence`, `Track`, `TrackItem`, `ProjectItem`, `Encoder`.

**Two parallel DOMs:**
- **Public DOM** (`app.project`, ExtendScript/UXP)
- **QE DOM** (`app.qe`, undocumented, reverse-engineered)

---

## DOM Hierarchy (Public)
---

## Object Types & Key Methods

### Application (app)

| Property/Method | Type | Notes |
|---|---|---|
| `app.project` | Project | Active project (read-only) |
| `app.encoder` | Encoder | Media Encoder integration |
| `app.quit()` | Method | Exit Premiere |
| `app.enableQE()` | Method | Enable undocumented QE DOM |

### Project

| Property/Method | Type | Notes |
|---|---|---|
| `project.name` | String | Project filename |
| `project.sequences` | SequenceCollection | All sequences |
| `project.projectItems` | ProjectItemCollection | All media items |
| `project.activeSequence` | Sequence | Currently open sequence |
| `project.createSequence()` | Method | Create new sequence |

### Sequence

| Property/Method | Type | Notes |
|---|---|---|
| `sequence.name` | String | Sequence name |
| `sequence.videoTracks` | TrackCollection | Video tracks |
| `sequence.audioTracks` | TrackCollection | Audio tracks |
| `sequence.markers` | MarkerCollection | Timeline markers |
| `sequence.duration` | Time | Total sequence length (in ticks) |
| `sequence.frameRate` | Number | Frames per second |

### Track

| Property/Method | Type | Notes |
|---|---|---|
| `track.clips` | TrackItemCollection | All clips on track |
| `track.insertClip()` | Method | Add clip to track |
| `track.locked` | Boolean | Track muted/locked state |

### TrackItem (Clip)

| Property/Method | Type | Notes |
|---|---|---|
| `trackItem.projectItem` | ProjectItem | Source media |
| `trackItem.inPoint` | Time | Start position (in ticks) |
| `trackItem.outPoint` | Time | End position (in ticks) |
| `trackItem.name` | String | Clip label |
| `trackItem.components` | ComponentCollection | Effects on clip |

### ProjectItem (Media)

| Property/Method | Type | Notes |
|---|---|---|
| `projectItem.name` | String | Filename/label |
| `projectItem.path` | String | File system path |
| `projectItem.duration` | Time | Media duration |
| `projectItem.videoFrameRate` | Number | Frame rate of media |
| `projectItem.type` | Number | Type enum (footage, sequence, etc.) |

### Time Object

Required for Premiere 14.1+:

```javascript
var seq = app.project.sequences[0];
var time = new Time();
time.seconds = 5;
seq.setZeroPoint(time);
```

---

## Accessing Objects

### ExtendScript Navigation

```javascript
var seq = app.project.sequences[0];
var track = seq.videoTracks[0];
var clip = track.clips[0];
var name = clip.name;
var inPoint = clip.inPoint.seconds;
var duration = clip.duration.ticks;
```

### UXP Navigation (Async)

```javascript
const { application } = require("premierepro");

(async () => {
  const proj = await application.activeProject;
  const seqs = await proj.sequences;
  const seq = seqs[0];
  const videoTracks = await seq.videoTracks;
  const track = videoTracks[0];
  const clips = await track.clips;
  const clip = clips[0];
  const name = await clip.name;
  const inPoint = await clip.inPoint;
  const inPointSeconds = await inPoint.seconds;
})();
```

---

## Collections & Iteration

```javascript
var numSeqs = app.project.sequences.numSequences;
for (var i = 0; i < numSeqs; i++) {
  var seq = app.project.sequences[i];
  alert(seq.name);
}
```

---

## Time & Ticks

**Ticks = Premiere's internal time unit:** 254,016,000,000 ticks/second.

```javascript
var seconds = ticks / 254016000000;
var ticks = seconds * 254016000000;
var time = new Time();
time.seconds = 5;
```

---

## Write-Only Limitations (ExtendScript)

**Some DOM writes only work in ExtendScript, NOT in CEP panels:**

- `track.locked = true`
- Clip rename via `trackItem.name = "..."`
- Sequence rename via `sequence.name = "..."`

**Workaround:** Use UXP (25.6+) for reliable write access via `executeTransaction()`.

---

## DOM Differences: ExtendScript vs UXP

| Feature | ExtendScript | UXP |
|---|---|---|
| Async | No | Yes (required) |
| Mutation wrapper | None | executeTransaction() |
| Undo steps | Automatic | Per-transaction |
| Errors | Exceptions | Promises rejection |
| DOM completeness | ~90% | ~80% |
| Recommended | Maintenance only | New work ✅ |

---

## Sources

- Premiere Pro Scripting Reference: https://ppro-scripting.docsforadobe.dev/
- UXP Documentation: https://developer.adobe.com/premiere-pro/uxp/
