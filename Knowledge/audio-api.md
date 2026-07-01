---
id: audio-api
title: Audio API - Mixing, Effects & Loudness
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app|qe
languages: [extendscript, uxp]
tags: [audio, mixing, loudness, ducking, effects, normalization]
related: [sequences-tracks-trackitems, reverse-engineering-qe-dom, export-rendering-media-encoder]
sources: ["https://ppro-scripting.docsforadobe.dev/", "Production testing: Premiere 25.x"]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Audio API - Mixing, Effects & Loudness

## TL;DR

Audio track/clip access via public DOM (ExtendScript/UXP) covers volume, mute, pan at the basic level. Effects-by-name (compressor, EQ, ducking presets) requires QE DOM, same limitation as video effects. Loudness normalization (LUFS) has no scripting API; must be done via Essential Sound panel UI or Audition round-trip.

Critical traps:
- No native LUFS/loudness API; Essential Sound panel is UI-only
- Audio effects by name: QE only (same as video)
- Track-level mute/solo writable in ExtendScript, partial in UXP 25.6
- Audio ducking (auto-ducking) is UI-driven, not scriptable directly

---

## Audio Track Access

```javascript
var seq = app.project.activeSequence;
var audioTrack = seq.audioTracks[0];

audioTrack.setMute(true);
audioTrack.setSolo(false);

var clip = audioTrack.clips[0];
var name = clip.name;
```

---

## Clip-Level Volume (Component-based)

Volume is exposed as a clip component, similar to video effects:

```javascript
var clip = seq.audioTracks[0].clips[0];

for (var i = 0; i < clip.components.numItems; i++) {
  var comp = clip.components[i];
  if (comp.displayName === "Volume") {
    for (var p = 0; p < comp.properties.numItems; p++) {
      var prop = comp.properties[p];
      if (prop.displayName === "Level") {
        prop.setValue(3.0, true);
      }
    }
  }
}
```

---

## Audio Effects By Name (QE Only)

Same limitation pattern as video effects — public API has no by-name lookup:

```javascript
app.enableQE();

var qeClip = app.qe.project.getActiveSequence().getAudioClipAt(0, 0);
var effectName = "Parametric Equalizer";

for (var i = 0; i < qeClip.getNumComponents(); i++) {
  var comp = qeClip.getComponentAt(i);
  if (comp.getName() === effectName) {
    console.log("Found: " + effectName);
    break;
  }
}
```

---

## Loudness Normalization (No Scripting API)

Premiere's Essential Sound panel performs LUFS-based loudness matching, but this is UI-only — no ExtendScript or UXP method exposes it.

**Workaround: External loudness normalization**

```python
import subprocess

subprocess.run([
    "ffmpeg", "-i", "input.wav",
    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
    "output_normalized.wav"
])
```

Re-import normalized audio after external processing.

---

## Auto-Ducking (UI Only)

Auto-ducking (lowering music under dialogue) is configured exclusively through the Essential Sound panel. No scripting hook exists in ExtendScript or UXP as of 25.6.

**Workaround:** Pre-process music stems externally with sidechain compression (e.g. via DAW or ffmpeg sidechaincompress filter), then import as a finished mix.

---

## Audio Gain & Normalize Clip (ExtendScript)

```javascript
var clip = seq.audioTracks[0].clips[0];
clip.setVolume(-3.0);
```

**Note:** This is a simplified gain stage, distinct from the Volume component's Level property; behavior may vary by Premiere version.

---

## UXP Audio Support (Emerging)

UXP 25.6 has partial read access to audio track metadata (name, mute state) but limited write/effect support. Full audio component manipulation expected in later UXP releases.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| Volume component not found | Clip has no explicit Volume component yet | Apply effect once via UI, then automate |
| Mute state not persisting (UXP) | Write not wrapped in executeTransaction() | Wrap mutation in transaction |
| LUFS value unreachable via API | No native loudness API | Use external ffmpeg loudnorm |
| Effect by name returns null | Public DOM, not QE | Switch to QE or iterate names manually |

---

## Sources

- Premiere Pro Scripting Reference: https://ppro-scripting.docsforadobe.dev/
- ffmpeg loudnorm filter docs
