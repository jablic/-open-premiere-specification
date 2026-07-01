---
id: markers
title: Markers & Timeline Annotations (Legacy Reference)
category: workflow
status: legacy
stability: active
doc_status: reference
introduced: "Premiere Pro CC 2015"
min_premiere_version: "14.0"
api_namespace: app
languages: [extendscript, uxp]
tags: [markers, annotations, timeline, cue-points, legacy-reference]
related: [markers-and-annotations]
superseded_by: [markers-and-annotations]
sources: [
  "https://ppro-scripting.docsforadobe.dev/",
  "Production workflows (Premiere 25.x)"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Markers & Timeline Annotations (Legacy Reference)

> **See markers-and-annotations.md for comprehensive, current documentation.** This document is a lightweight legacy reference. New projects should use the full markers-and-annotations guide.

## TL;DR

**Markers = timeline cue points with custom data.** Add via Marker menu or ExtendScript. Supports color coding, duration, custom text, comments. **Limits:** No nested markers, marker data non-standard (varies by type).

---

## Marker Types

| Type | Purpose | Accessible via |
|---|---|---|
| Comment Marker | Notes/comments | ExtendScript, UXP |
| Chapter Marker | DVD/timeline chapters | ExtendScript only |
| Segmentation Marker | Adobe Prelude (legacy) | ExtendScript |
| Web Link Marker | URLs (legacy) | ExtendScript |

---

## Create Marker (ExtendScript)

```javascript
var seq = app.project.activeSequence;
var markerCollection = seq.markers;

var marker = markerCollection.createMarker(254016000000);
marker.name = "Scene Start";
marker.comments = "Important transition here";
marker.setColorByIndex(2);
```

---

## Read Markers (ExtendScript)

```javascript
var seq = app.project.activeSequence;
var markerCollection = seq.markers;

for (var i = 0; i < markerCollection.numMarkers; i++) {
  var marker = markerCollection.getMarker(i);
  var time = marker.startTime;
  var name = marker.name;
  console.log(name + " @ " + time);
}
```

---

## Marker Colors

```javascript
marker.setColorByIndex(0);
```

Color indices: 0=No Color, 1=Red, 2=Pink, 3=Purple, 4=Blue, 5=Cyan, 6=Green, 7=Yellow, 8=Orange.

---

## UXP Marker Support (Emerging)

Limited in UXP 25.6. Full API expected in 26.x.

---

## Sources

- Marker API: https://ppro-scripting.docsforadobe.dev/
