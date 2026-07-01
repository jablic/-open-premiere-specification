---
id: multicam-api
title: Multicam Sequences - Sync, Switching & ASE
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app|qe
languages: [extendscript, uxp]
tags: [multicam, sync, angle-editor, ase, camera-switching]
related: [sequences-tracks-trackitems, reverse-engineering-qe-dom, automation]
sources: ["Production testing: Premiere 25.x", "Community findings"]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Multicam Sequences - Sync, Switching & ASE

## TL;DR

Multicam sequence creation (`createMulticamSequence` equivalent) and angle synchronization are primarily UI-driven; public API has no direct "create multicam from clips with audio sync" call. Once a multicam sequence exists, angle switching during edit (Angle Switcher) is also UI-only. Programmatic camera-cut assembly is achievable only by manually positioning clips with matching inPoint/outPoint values calculated from sync markers, not via a dedicated multicam API.

Critical traps:
- No public API for "auto-sync by audio waveform" — must rely on UI-created multicam source sequence
- Angle switching during playback (Angle Switcher) is UI-only
- Multicam source sequences ARE regular sequences underneath — accessible like any Sequence object
- Camera cut points can be reconstructed via marker positions, but this is a manual technique, not a native API

---

## What "Multicam" Actually Is (DOM-Level)

A multicam sequence is implemented as a nested Sequence containing synced camera angle tracks. There is no distinct `MulticamSequence` class — once created (via UI), it behaves as a regular `Sequence` object with multiple video tracks representing angles.

```javascript
var seq = app.project.activeSequence;
console.log(seq.name);
console.log(seq.videoTracks.numTracks);
```

---

## Manual Camera Sync (Without Native API)

Since no API performs audio-waveform sync, a common pattern is marker-based manual alignment:

```javascript
var proj = app.project;
var seq = proj.activeSequence;

var cameras = [
  seq.videoTracks[0].clips[0],
  seq.videoTracks[1].clips[0],
  seq.videoTracks[2].clips[0]
];

var syncPoint = new Time();
syncPoint.seconds = 0;

for (var i = 0; i < cameras.length; i++) {
  cameras[i].inPoint = syncPoint;
}
```

**Limitation:** This sets a common start point, not audio-waveform-accurate sync. For accurate sync, create the multicam sequence via UI first (File > New > Multi-Camera Source Sequence), then script against the resulting Sequence object.

---

## Working With an Existing Multicam Sequence

Once created in UI, the resulting nested sequence can be scripted like any other:

```javascript
var multicamSeq = app.project.sequences[1];

for (var i = 0; i < multicamSeq.videoTracks.numTracks; i++) {
  var track = multicamSeq.videoTracks[i];
  console.log("Angle " + i + ": " + track.clips.numItems + " clips");
}
```

---

## Angle Switching (UI Only — No API)

The Angle Switcher / Multi-Camera Monitor used for live camera-cut editing has no scripting hook in ExtendScript or UXP 25.6. Cut decisions made during multicam editing on the timeline produce ordinary TrackItem edits on the resulting flattened sequence — those edits ARE scriptable after the fact, just not the live-switching action itself.

---

## Post-Multicam Flattened Sequence

After "Flatten" is applied (collapsing multicam into a single-camera cut sequence), the result is a normal sequence with standard clip editing API access:

```javascript
var flatSeq = app.project.activeSequence;
var track = flatSeq.videoTracks[0];

for (var i = 0; i < track.clips.numItems; i++) {
  var clip = track.clips[i];
  console.log(clip.name + " starts at " + clip.inPoint.seconds);
}
```

---

## QE Fallback for Angle Metadata

```javascript
app.enableQE();
var qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);
```

**Note:** QE does not expose multicam-specific metadata beyond standard clip/component access; no special angle-aware methods found in reverse engineering to date.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| Sync drifts across cameras | Manual inPoint sync, not waveform-accurate | Create multicam via UI sync first |
| Angle Switcher has no script hook | UI-only feature | Script the flattened result instead |
| Multicam sequence not found in project.sequences | Created but not yet selected/indexed | Iterate all sequences, check track count heuristically |

---

## Sources

- Production testing: Premiere 25.x
- Community findings (forums, multicam scripting threads)
