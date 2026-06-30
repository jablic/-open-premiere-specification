---
id: automation
title: Automation & Scripting
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app
languages: [extendscript, uxp, python]
tags: [automation, scripting, workflow, batch-processing]
related: [extendscript-core, uxp, best-practices, export-rendering-media-encoder]
sources: [
  "https://ppro-scripting.docsforadobe.dev/",
  "Production workflows (Premiere 25.x)",
  "Community scripts (bbb999, Adobe forums)"
]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Automation & Scripting

## TL;DR

**Automation = ExtendScript (legacy), UXP (modern), or external scripts (Python, shell).** Use for batch processing, repetitive tasks, workflow optimization. **ExtendScript:** Freezing Sept 2026. **UXP:** Recommended for new work (async, modern). **External:** Python + FCPXML export/import or CLI tools.

**Critical traps:**
- ExtendScript blocks UI (no async)
- UXP requires `executeTransaction()` for mutations
- File paths may break cross-platform (use Path.join)
- Undo stack grows with large operations (batch in transactions)

---

## Automation Paths

### Path 1: ExtendScript (Legacy)

Synchronous, blocking UI. EOL Sept 2026.

```javascript
var proj = app.project;
var seq = proj.activeSequence;

for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
  var clip = seq.videoTracks[0].clips[i];
  clip.name = clip.name + " [Edited]";
}

alert("Done!");
```

**Pros:** Simple, immediate results
**Cons:** Blocks UI, no async, deprecated

### Path 2: UXP (Modern, Recommended)

Async-first, non-blocking. Premiere 25.6+.

```javascript
const { application } = require("premierepro");

(async () => {
  const proj = await application.activeProject;
  const seq = await proj.activeSequence;
  
  await application.executeTransaction(async () => {
    const videoTracks = await seq.videoTracks;
    const track = videoTracks[0];
    const clips = await track.clips;
    
    for (let i = 0; i < clips.length; i++) {
      const clip = clips[i];
      const name = await clip.name;
      await clip.setName(name + " [Edited]");
    }
  });
  
  console.log("Done!");
})();
```

**Pros:** Async, non-blocking, modern, recommended
**Cons:** Learning curve, requires UXP environment

### Path 3: External Scripts (Python/Shell)

Operate on exported XML or via CLI. Platform-independent.

```python
import xml.etree.ElementTree as ET

tree = ET.parse('project.xml')
root = tree.getroot()

for clipitem in root.findall('.//clipitem'):
  name = clipitem.findtext('name')
  new_name = name + " [Edited]"
  name_elem = clipitem.find('name')
  name_elem.text = new_name

tree.write('project_edited.xml')
print("Done!")
```

**Pros:** Works outside Premiere, batch processing
**Cons:** Requires re-import, limited metadata access

---

## Batch Processing Patterns

### Pattern 1: Batch Rename Clips

```javascript
const { application } = require("premierepro");

(async () => {
  const proj = await application.activeProject;
  
  await application.executeTransaction(async () => {
    const items = await proj.projectItems;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const name = await item.name;
      if (name.includes("RENAME_ME")) {
        await item.setName(name.replace("RENAME_ME", "RENAMED"));
      }
    }
  });
})();
```

### Pattern 2: Batch Export Sequences

```javascript
var proj = app.project;
var presets = app.encoder.getExportPresets();

for (var i = 0; i < proj.sequences.numSequences; i++) {
  var seq = proj.sequences[i];
  var outputPath = "/Volumes/exports/" + seq.name + ".mp4";
  
  app.encoder.encodeFile(seq, presets[0], outputPath, 
    true, true);
}
```

### Pattern 3: Batch Add Effects

```javascript
app.enableQE();

var seq = app.project.activeSequence;
var effectName = "Lumetri Color";

for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
  var clip = seq.videoTracks[0].clips[i];
  var effect = clip.createComponent(effectName);
}
```

---

## Error Handling

### ExtendScript Try/Catch

```javascript
try {
  var seq = app.project.activeSequence;
  if (!seq) throw new Error("No active sequence");
  
  for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
    var clip = seq.videoTracks[0].clips[i];
    clip.name = clip.name + " [OK]";
  }
} catch (err) {
  alert("Error: " + err.message);
}
```

### UXP Async Error Handling

```javascript
const { application } = require("premierepro");

(async () => {
  try {
    const proj = await application.activeProject;
    if (!proj) throw new Error("No active project");
    
    await application.executeTransaction(async () => {
      const seq = await proj.activeSequence;
      // operations...
    });
  } catch (error) {
    console.error("Automation error:", error.message);
  }
})();
```

---

## Performance Tips

1. **Batch in transactions:** Wrap large edits in single `executeTransaction()`
2. **Avoid redundant reads:** Cache properties locally
3. **Use collections efficiently:** Pre-fetch arrays, iterate once
4. **Log progress:** For long operations, log every Nth item
5. **Test on small projects first:** Catch errors early

---

## Undo / Redo

**ExtendScript:** Auto-grouped under single undo step
**UXP:** Per-transaction undo step (use `executeTransaction()`)

```javascript
await application.executeTransaction(async () => {
  await clip1.setName("Clip A");
  await clip2.setName("Clip B");
});
```

Single undo step for both edits.

---

## Sources

- Premiere Pro Scripting Reference: https://ppro-scripting.docsforadobe.dev/
- UXP Plugins Guide: https://developer.adobe.com/premiere-pro/uxp/
