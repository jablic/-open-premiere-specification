---
id: best-practices
title: Best Practices & Anti-Patterns
category: reference
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [extendscript, uxp]
tags: [best-practices, anti-patterns, performance, reliability]
related: [extendscript-core, uxp, automation, cep]
sources: [
  "Production experience (15+ years post-production)",
  "Community findings (forums, scripting groups)",
  "Adobe best practices documentation"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Best Practices & Anti-Patterns

## TL;DR

**Do:** Error handling, test on small projects, batch operations, use async (UXP), cache properties. **Don't:** Assume UI always available, ignore undo/redo, hardcode paths, use QE without disclaimers, assume cross-version compatibility.

---

## Production Best Practices

### 1. Always Use Error Handling

```javascript
try {
  var seq = app.project.activeSequence;
  if (!seq) throw new Error("No active sequence");
  
  for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
    var clip = seq.videoTracks[0].clips[i];
  }
} catch (err) {
  alert("Script failed: " + err.message);
  $.quit();
}
```

### 2. Test on Small Project First

Never run batch operations on production files. Test on:
- Minimal sequence (1–2 clips)
- Verify undo/redo works
- Check for data loss

### 3. Cache Properties Locally

```javascript
var seq = app.project.activeSequence;
var numTracks = seq.videoTracks.numTracks;
var numClips = seq.videoTracks[0].clips.length;

for (var i = 0; i < numClips; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
```

**Not:**
```javascript
for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
```

### 4. Batch Operations in Transactions (UXP)

```javascript
await application.executeTransaction(async () => {
  await clip1.setName("A");
  await clip2.setName("B");
  await clip3.setName("C");
});
```

Single undo step = better UX.

### 5. Log Progress for Long Operations

```javascript
var total = seq.videoTracks[0].clips.length;
for (var i = 0; i < total; i++) {
  if (i % 10 === 0) {
    console.log("Progress: " + i + "/" + total);
  }
  var clip = seq.videoTracks[0].clips[i];
}
```

### 6. Use Absolute Paths (Cross-Platform)

```javascript
var path = "~/Desktop/export.mp4";
var absPath = new File(path).fsName;
```

**Not:**
```javascript
var path = "/Users/user/Desktop/export.mp4";
```

### 7. Handle Missing Objects Gracefully

```javascript
var seq = app.project.activeSequence;
if (!seq) {
  console.log("No active sequence");
  return;
}

var track = seq.videoTracks[0];
if (!track || track.clips.length === 0) {
  console.log("No clips in first video track");
  return;
}
```

### 8. Document UXP Async Requirements

```javascript
const { application } = require("premierepro");

(async () => {
  const proj = await application.activeProject;
  if (!proj) {
    console.error("No active project");
    return;
  }
  
  await application.executeTransaction(async () => {
  });
})();
```

**Comment:** "All `await` required; no sync access to DOM."

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Forgetting `await` (UXP)

```javascript
const proj = application.activeProject;
const name = await proj.name;
```

**Result:** `proj` is a Promise, not a Project object.

**Fix:** `const proj = await application.activeProject;`

---

### ❌ Anti-Pattern 2: Mutation Without `executeTransaction()` (UXP)

```javascript
await clip.setName("New Name");
```

**Result:** Undo/redo may not work correctly.

**Fix:**
```javascript
await application.executeTransaction(async () => {
  await clip.setName("New Name");
});
```

---

### ❌ Anti-Pattern 3: Assuming UI Context in ExtendScript

```javascript
var clip = app.project.activeSequence.videoTracks[0].clips[0];
clip.name = "Test";
```

**Result:** Fails if no active sequence or in panel context.

**Fix:** Check preconditions; use UXP for reliable UI context.

---

### ❌ Anti-Pattern 4: Hardcoded Paths

```javascript
var path = "/Users/konstantin/Desktop/export.mp4";
```

**Result:** Breaks on different machines.

**Fix:** Use environment variables or UI file picker.

---

### ❌ Anti-Pattern 5: Using QE Without Warning

```javascript
app.enableQE();
var qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);
qeClip.setSpeed(0.5);
```

**Result:** User thinks it's stable API; breaks in Premiere 26.

**Fix:** Document risk; add disclaimer in UI/log.

---

### ❌ Anti-Pattern 6: Ignoring Version Differences

```javascript
var time = new Time();
time.seconds = 5;
```

**Result:** Fails in Premiere < 14.1.

**Fix:** Version-check; use ticks as fallback.

---

### ❌ Anti-Pattern 7: Large Batch Without Progress Feedback

```javascript
for (var i = 0; i < 10000; i++) {
  clip[i].name = "Clip " + i;
}
```

**Result:** UI freezes; user thinks script crashed.

**Fix:** Log every N iterations; use progress indicator (CEP).

---

### ❌ Anti-Pattern 8: Not Testing Undo/Redo

```javascript
script does edits;
```

**Result:** Undo broken; user manually reverts.

**Fix:** After each script, test undo. Verify undo stack is clean.

---

## Performance Tips

| Tip | Impact | Effort |
|---|---|---|
| Cache property reads | 10–50% faster | Low |
| Batch in transactions | Better UX | Low |
| Limit DOM queries | 20–30% faster | Medium |
| Use QE only if necessary | Avoid instability | Low |
| Test on small project first | Prevent data loss | Low |

---

## Reliability Checklist

- [ ] Error handling on all operations
- [ ] Tested on small project
- [ ] Properties cached locally
- [ ] Mutations in `executeTransaction()` (UXP)
- [ ] Version checks for API calls
- [ ] Cross-platform paths (absolute)
- [ ] Progress logging for >1000 items
- [ ] Undo/redo works correctly
- [ ] No hardcoded user paths
- [ ] QE disclaimer (if used)

---

## Sources

- Adobe best practices: https://ppro-scripting.docsforadobe.dev/
- Community findings: Adobe forums, scripting groups
- Production experience: Documented pitfalls from real-world use
