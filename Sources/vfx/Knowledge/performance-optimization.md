---
id: performance-optimization
title: Performance & Optimization Patterns
category: advanced
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [extendscript, uxp, python]
tags: [performance, optimization, caching, batching, profiling]
related: [automation, best-practices, extendscript-core, uxp]
sources: ["Production workflows", "Benchmarking (Premiere 25.x)"]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Performance & Optimization Patterns

## TL;DR

**Optimization = batching + caching + async.** For 100+ clips: batch in transactions. For 1000+ items: split into parallel batches. For real-time: use C++ or QE (risky). Profile first; don't guess.

---

## Profiling Patterns

### ExtendScript Timer

```javascript
var start = new Date();
for (var i = 0; i < 1000; i++) {
  var clip = seq.videoTracks[0].clips[i];
  clip.name = "Clip " + i;
}
var elapsed = new Date() - start;
alert("Time: " + elapsed + "ms");
```

### UXP Profiling

```javascript
console.time("batch-operation");
await application.executeTransaction(async () => {
  for (let i = 0; i < 1000; i++) {
    await processBatch(i);
  }
});
console.timeEnd("batch-operation");
```

---

## Batching Strategies

### Small Batch (< 100 items)

```javascript
await application.executeTransaction(async () => {
  const clips = await track.clips;
  for (let i = 0; i < clips.length; i++) {
    await clips[i].setName("Batch " + i);
  }
});
```

### Large Batch (100-10000 items)

```javascript
const BATCH_SIZE = 100;
const clips = await track.clips;

for (let start = 0; start < clips.length; start += BATCH_SIZE) {
  const end = Math.min(start + BATCH_SIZE, clips.length);
  await application.executeTransaction(async () => {
    for (let i = start; i < end; i++) {
      await clips[i].setName("Batch " + i);
    }
  });
  console.log("Progress: " + end + "/" + clips.length);
}
```

---

## Caching Patterns

### Property Caching

```javascript
var seq = app.project.activeSequence;
var numClips = seq.videoTracks[0].clips.length;
for (var i = 0; i < numClips; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
```

Not:
```javascript
for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
```

---

## GPU Acceleration

No direct GPU API in Premiere. Workaround via external ffmpeg with CUDA hwupload, processed outside Premiere then re-imported.

---

## Parallel Processing (External)

```python
from multiprocessing import Pool

def process_clip(clip_path):
    return transcode(clip_path)

clips = ["clip1.mov", "clip2.mov", "clip3.mov"]
with Pool(4) as p:
    results = p.map(process_clip, clips)
```

---

## Sources

- Adobe Premiere Pro Performance docs
