---
id: color-management
title: Color Management - Lumetri, LUTs & Color Spaces
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: app|qe
languages: [extendscript, uxp]
tags: [color, lumetri, lut, color-space, grading, hdr]
related: [essential-graphics-mogrt-text, reverse-engineering-qe-dom, export-rendering-media-encoder]
sources: ["Production testing: Premiere 25.x", "Adobe Color documentation"]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Color Management - Lumetri, LUTs & Color Spaces

## TL;DR

Lumetri Color is applied as a clip component (same pattern as any effect); individual sub-parameters (Basic Correction sliders, Color Wheels, Curves) are accessible as nested properties but the parameter ID map is undocumented and version-fragile. LUT application is supported via file path parameter. Color space conversion (Rec.709 vs Rec.2020 vs HDR) is project/sequence-level setting, not easily scriptable.

Critical traps:
- Lumetri parameter names/IDs are undocumented and can shift between Premiere versions
- LUT must be a valid file path; relative paths often fail — use absolute paths
- HDR/Wide Gamut sequence settings are mostly UI-only at the project level
- Color space tagging on footage (e.g. Rec.709 vs Log) affects rendering but isn't exposed cleanly via scripting

---

## Apply Lumetri Color (Basic)

```javascript
var clip = seq.videoTracks[0].clips[0];
var lumetri = clip.createComponent("Lumetri Color");

if (lumetri) {
  console.log("Lumetri applied");
}
```

---

## Set Lumetri Parameters (Undocumented IDs)

Parameter names must be matched by display name; there is no stable numeric ID guaranteed across versions.

```javascript
var clip = seq.videoTracks[0].clips[0];

for (var i = 0; i < clip.components.numItems; i++) {
  var comp = clip.components[i];
  if (comp.displayName === "Lumetri Color") {
    for (var p = 0; p < comp.properties.numItems; p++) {
      var prop = comp.properties[p];
      if (prop.displayName.indexOf("Saturation") !== -1) {
        prop.setValue(120, true);
      }
      if (prop.displayName.indexOf("Contrast") !== -1) {
        prop.setValue(10, true);
      }
    }
  }
}
```

**Gotcha:** Sub-panel parameters (Curves, Color Wheels, HSL Secondary) are nested deeper and not reliably enumerable; treat as low-confidence automation target.

---

## Apply LUT File

```javascript
var clip = seq.videoTracks[0].clips[0];
var lumetri = clip.createComponent("Lumetri Color");

for (var p = 0; p < lumetri.properties.numItems; p++) {
  var prop = lumetri.properties[p];
  if (prop.displayName === "Input LUT") {
    prop.setValue("/Volumes/LUTs/Rec709_to_LogC.cube", true);
  }
}
```

**Requirement:** Absolute file path. Relative paths frequently fail to resolve depending on context (panel vs script).

---

## Color Space & Sequence Settings

Sequence color space (working color space, HDR tone mapping) is set in Sequence Settings dialog. No reliable ExtendScript/UXP API exposes this as of 25.6.

```javascript
var seq = app.project.activeSequence;
console.log(seq.name);
```

**Workaround:** For batch color-space-consistent sequence creation, duplicate a pre-configured sequence template via `project.createSequence()` and copy from a known-good preset, rather than setting color space programmatically.

---

## HDR Workflow Notes

- Rec.2020 / PQ / HLG tone mapping configured per-sequence in UI
- Export to HDR formats requires matching Media Encoder preset (no direct API control over tone-mapping curve)
- Round-trip via DaVinci Resolve XML loses HDR metadata (see xml-fcpxml.md limitations)

---

## QE Color Component Access (Fallback)

```javascript
app.enableQE();

var qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);
var lumetriComp = qeClip.getComponentByName("Lumetri Color");

if (lumetriComp) {
  console.log("QE Lumetri component found");
}
```

Use only if public DOM component access fails (rare); same undocumented-API risk as other QE usage.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| LUT not applying | Relative path used | Use absolute file path |
| Parameter not found | Display name changed between versions | Log all property names first, match by substring |
| Color space changes ignored | No sequence-level scripting API | Use pre-configured sequence template |
| Curves/Color Wheels inaccessible | Deeply nested UI-only controls | Treat as manual-only; document limitation |

---

## Sources

- Production testing: Premiere 25.x
- Adobe Color documentation (LUT format specs)
