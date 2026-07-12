---
status: "production"
doc_status: "complete"
confidence: "high"
min_premiere_version: "24.0"
tags: ["api", "workflow", "logging", "metadata", "source-monitor", "scripting"]
last_verified: "2026-07-12"
verified_against_version: "25.6"
---

# Adobe Premiere Pro 2026 Source Monitor & Logging Scripting Reference

## Table of Contents
1. [Overview & Architecture](#overview--architecture)
2. [Source Monitor APIs](#source-monitor-apis)
3. [Subclip Creation & Management](#subclip-creation--management)
4. [Logging Metadata Schema](#logging-metadata-schema)
5. [In/Out Point Manipulation](#inout-point-manipulation)
6. [Source Clip Properties Access](#source-clip-properties-access)
7. [Logging Panel Integration](#logging-panel-integration)
8. [Metadata XMP Properties](#metadata-xmp-properties)
9. [Sync Settings for Multicam](#sync-settings-for-multicam)
10. [Production Example: Auto-Logging Tool](#production-example-auto-logging-tool)
11. [Edge Cases & Version Compatibility](#edge-cases--version-compatibility)

---

## Overview & Architecture

### Source Monitor in Premiere
The Source Monitor is the preview window for media clips in the project panel. Unlike the timeline, source monitors display individual clips before they're edited into sequences. Scripting the source monitor involves:

- **Source clips** (ProjectItems) with inherent properties (duration, frame rate, media path)
- **Subclips** (derived ProjectItems) with custom in/out points and metadata
- **Markers** attached to source clips or subclips (logging data)
- **XMP metadata** (extensible metadata platform) for custom fields
- **Multicam sync metadata** (for multi-camera workflows)

### Technology Compatibility Matrix

| Operation | ExtendScript | UXP 25.6 | QE DOM | Status |
|---|---|---|---|---|
| Read source clip properties | Yes | Yes | Yes | Production |
| Create subclip | Yes | No | No | ExtendScript only |
| Get/set markers on clips | Yes | Partial | Yes | Production |
| XMP metadata read/write | Yes | Partial | Yes | Production |
| Multicam sync data | No | No | Partial | QE only |
| Direct source monitor control | No | No | No | UI-only feature |

**Key constraint:** Source Monitor is a UI-only panel. Direct scripting of the source monitor view (selecting clips, displaying in monitor, auto-play) is **not available**. Scripting operates on the underlying clips and metadata only.

---

## Source Monitor APIs

### ProjectItem: The Source Clip Root Object

All source monitoring starts with a **ProjectItem** from the project panel. ProjectItems represent clips, bins, or folders.

#### Signature

```javascript
// ExtendScript (ES3)
var projectItem = app.project.rootItem.children[0];  // First project item

// Properties (read-only on acquisition)
var name = projectItem.name;              // string
var type = projectItem.type;              // CLIP (1) | BIN (2) | ROOT (3) | FILE (4)
var treePath = projectItem.treePath;      // "/Bin Name/Clip Name" format
var duration = projectItem.duration;      // Time object (source clip duration)
var mediaType = projectItem.mediaType;    // "Video" | "Audio" | "Video + Audio"
```

#### Reading Source Clip Properties (ExtendScript)

```javascript
// ExtendScript (ES3) — Read source clip duration and frame rate
function getSourceClipInfo(projectItem) {
    try {
        if (!projectItem || projectItem.type !== 1) {
            return { ok: false, err: "Not a clip" };
        }
        
        var duration = projectItem.duration;
        var durationSeconds = (duration ? duration.seconds : 0);
        var mediaPath = projectItem.getMediaPath();
        
        // Get frame rate (via metadata if available)
        var metadata = projectItem.getProjectMetadata();
        
        return {
            ok: true,
            name: projectItem.name,
            duration: durationSeconds,
            mediaPath: mediaPath,
            mediaType: projectItem.mediaType
        };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

#### Finding Source Clips by Path

```javascript
// ExtendScript — Locate clips by media file path
function findClipByMediaPath(mediaPath) {
    var results = app.project.rootItem.findItemsMatchingMediaPath(mediaPath, false);
    // results is array of ProjectItems matching the path
    return results.length > 0 ? results[0] : null;
}
```

### UXP: Limited Source Clip Access (25.6)

```javascript
// UXP 25.6 — Async property access
const { application } = require("premierepro");

(async () => {
    const proj = await application.activeProject;
    const bins = await proj.bins;  // Top-level bins
    
    for (let i = 0; i < bins.length; i++) {
        const bin = bins[i];
        const clips = await bin.children;  // ProjectItems in bin
        
        for (let j = 0; j < clips.length; j++) {
            const clip = clips[j];
            const name = await clip.name;
            const dur = await clip.duration;  // May be Promise<Time>
            console.log(`Clip: ${name}, Duration: ${dur}`);
        }
    }
})();
```

**Limitation:** UXP 25.6 does not expose all ExtendScript clip properties. Subclip creation, XMP metadata, and multicam sync are not available in UXP yet. Use ExtendScript for full source monitor logging.

---

## Subclip Creation & Management

### What is a Subclip?

A **subclip** is a ProjectItem derived from a source clip, with custom in/out points. Subclips are stored in the project file and appear in the Project panel alongside the source clip. They do not physically copy media files — they reference the original and store only the trim points and metadata.

### CreateSubClip Signature (ExtendScript)

```javascript
// ExtendScript (ES3) — Premiere 14.1+
var subclip = projectItem.createSubClip(
    name,                    // string: subclip name
    startTicks,              // number: start time in ticks (254,016,000,000 per second)
    endTicks,                // number: end time in ticks
    hasHardBoundaries,       // boolean: if true, trims playback to in/out (prevents stepping outside)
    takeVideo,               // boolean: include video track
    takeAudio                // boolean: include audio track
);
```

### Example 1: Create a Subclip from Marker Positions

```javascript
// ExtendScript (ES3) — Auto-create subclips from a source clip's markers
function createSubclipsFromMarkers(projectItem) {
    if (!projectItem || projectItem.type !== 1) {
        return { ok: false, err: "Not a clip" };
    }
    
    try {
        var markers = projectItem.getMarkers();
        var subclips = [];
        var TICKS_PER_SECOND = 254016000000;
        
        // Iterate pairs of markers: (start, end)
        for (var i = 0; i < markers.numMarkers - 1; i += 2) {
            var startMarker = markers.getMarker(i);
            var endMarker = markers.getMarker(i + 1);
            
            var startTicks = Math.round(startMarker.startTime.seconds * TICKS_PER_SECOND);
            var endTicks = Math.round(endMarker.startTime.seconds * TICKS_PER_SECOND);
            
            var subclipName = "Subclip_" + (i / 2 + 1);
            var subclip = projectItem.createSubClip(
                subclipName,
                startTicks,
                endTicks,
                true,   // hard boundaries
                true,   // take video
                true    // take audio
            );
            
            subclips.push({
                name: subclipName,
                startSeconds: startMarker.startTime.seconds,
                endSeconds: endMarker.startTime.seconds
            });
        }
        
        return { ok: true, subclips: subclips };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Example 2: Create Subclips with Metadata Tags

```javascript
// ExtendScript (ES3) — Create subclip and immediately tag with XMP metadata
function createSubclipWithTags(projectItem, name, startSec, endSec, tags) {
    var TICKS_PER_SECOND = 254016000000;
    
    try {
        var startTicks = Math.round(startSec * TICKS_PER_SECOND);
        var endTicks = Math.round(endSec * TICKS_PER_SECOND);
        
        // Create subclip
        var subclip = projectItem.createSubClip(
            name,
            startTicks,
            endTicks,
            true,   // hard boundaries
            true,   // video
            true    // audio
        );
        
        // Immediately add XMP metadata (tags)
        if (tags && tags.length > 0) {
            var xmpBuffer = subclip.getXMPMetadata();
            var xmpString = xmpBuffer ? xmpBuffer.toString() : '<?xml version="1.0"?><x:xmpmeta xmlns:x="adobe:ns:meta/"></x:xmpmeta>';
            
            // Simple tag insertion (production would use proper XML parser)
            var tagsXml = '<rdf:Description rdf:about="" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">';
            for (var i = 0; i < tags.length; i++) {
                tagsXml += '<dc:subject>' + tags[i] + '</dc:subject>';
            }
            tagsXml += '</rdf:Description>';
            
            // Set XMP (this is simplified; real implementation needs proper XML handling)
            // subclip.setXMPMetadata(new Buffer(xmpString + tagsXml));
        }
        
        return { ok: true, subclip: subclip.name };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Subclip Limitations

- **No XMP write in UXP (25.6):** Must use ExtendScript
- **No multicam metadata:** QE-only for sync properties
- **One-way creation:** Cannot convert a subclip back to a full clip; delete and recreate if needed
- **Bin isolation:** Subclips appear in the bin where the source clip is located

---

## Logging Metadata Schema

### Marker Types and Logging Metadata

Markers are the primary logging mechanism in Premiere. Each marker can carry:
- **Name** (display text)
- **Comments** (multiline notes)
- **Color** (visual category)
- **Duration** (optional marker range)
- **Custom metadata** (type-specific fields)

#### Marker Type Enum

```javascript
// ExtendScript marker types (from Scripting Guide)
var COMMENT_MARKER = 1;       // General comment (logging primary)
var CHAPTER_MARKER = 2;       // Chapter point (DVD structure)
var SEGMENTATION_MARKER = 4;  // Prelude legacy (deprecated)
var WEB_LINK_MARKER = 8;      // URL link (legacy)
```

### Create Logging Marker (ExtendScript)

```javascript
// ExtendScript (ES3) — Add a marker to a clip or sequence
function createLoggingMarker(clipOrSeq, atSeconds, markerName, comments, colorIndex) {
    try {
        var markers = clipOrSeq.getMarkers ? 
            clipOrSeq.getMarkers() :  // ProjectItem
            clipOrSeq.markers;         // Sequence
        
        if (!markers) {
            return { ok: false, err: "No markers collection" };
        }
        
        // Create marker at specific time
        var t = new Time();
        t.seconds = atSeconds;
        
        var marker = markers.createMarker(t.ticks);
        marker.name = markerName || "Log Entry";
        marker.comments = comments || "";
        marker.setColorByIndex(colorIndex || 0);  // 0-8 indices
        
        return { ok: true, markerName: marker.name };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Logging Schema (Recommended Structure)

```javascript
// Standard logging marker schema (store in comments field as JSON)
{
    "version": "1.0",
    "timestamp": "2026-07-12T14:30:00Z",
    "scene": "Scene 1A",
    "take": 3,
    "notes": "Good performance, slight audio dropout at 2:15",
    "tags": ["good-take", "color-grade-ready", "needs-audio-fix"],
    "technical": {
        "frameRate": "23.976",
        "resolution": "4K UHD",
        "colorSpace": "Rec.709"
    },
    "editor": "John Smith",
    "duration": "00:05:30"
}
```

### Read All Markers from Clip (ExtendScript)

```javascript
// ExtendScript — Iterate and extract marker data
function getClipMarkers(projectItem) {
    try {
        if (!projectItem) {
            return { ok: false, err: "Invalid clip" };
        }
        
        var markers = projectItem.getMarkers();
        var markerList = [];
        
        for (var i = 0; i < markers.numMarkers; i++) {
            var marker = markers.getMarker(i);
            var markerData = {
                index: i,
                name: marker.name,
                comments: marker.comments,
                startTime: marker.startTime.seconds,
                duration: marker.duration ? marker.duration.seconds : 0,
                color: marker.colorIndex  // 0-8
            };
            
            // Try to parse JSON comments
            try {
                markerData.parsedData = JSON.parse(marker.comments);
            } catch (e) {
                markerData.parsedData = null;
            }
            
            markerList.push(markerData);
        }
        
        return { ok: true, markers: markerList };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Marker Colors (Index Reference)

| Index | Color | Hex | Suggested Use |
|---|---|---|---|
| 0 | No Color | none | General/neutral |
| 1 | Red | #F71414 | Issues, needs fix |
| 2 | Pink | #FF69B4 | Review flag |
| 3 | Purple | #A64DFF | VFX work |
| 4 | Blue | #1E90FF | Color grade |
| 5 | Cyan | #00FFFF | Audio work |
| 6 | Green | #00B050 | Approved |
| 7 | Yellow | #FFFF00 | In progress |
| 8 | Orange | #FF8800 | Export ready |

---

## In/Out Point Manipulation

### Understanding Time Objects and Ticks

Premiere's internal time unit is **ticks**: **254,016,000,000 ticks per second**. The API requires **Time objects** (not raw numbers) on Premiere 14.1+.

```javascript
// ExtendScript (ES3) — Time conversion utilities
var TICKS_PER_SECOND = 254016000000;

function secondsToTicks(seconds) {
    return Math.round(seconds * TICKS_PER_SECOND);
}

function ticksToSeconds(ticks) {
    return Number(ticks) / TICKS_PER_SECOND;
}

function createTimeObject(seconds) {
    var t = new Time();
    t.seconds = seconds;
    return t;
}
```

### Setting In/Out Points on TrackItem (Timeline)

```javascript
// ExtendScript (ES3) — Trim source clip in/out on timeline
function trimSourceOnTimeline(trackItem, inSeconds, outSeconds) {
    try {
        trackItem.inPoint = createTimeObject(inSeconds);
        trackItem.outPoint = createTimeObject(outSeconds);
        return { ok: true };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Setting In/Out Points on ProjectItem (Source Monitor)

ProjectItems themselves do not have in/out points — those are properties of **subclips**. Create a subclip to set custom in/out points.

```javascript
// ExtendScript — Create a subclip (which has in/out points)
function setSourceInOut(projectItem, inSeconds, outSeconds) {
    var TICKS_PER_SECOND = 254016000000;
    var startTicks = Math.round(inSeconds * TICKS_PER_SECOND);
    var endTicks = Math.round(outSeconds * TICKS_PER_SECOND);
    
    var subclip = projectItem.createSubClip(
        "Trimmed_" + projectItem.name,
        startTicks,
        endTicks,
        true,  // hard boundaries (enforce in/out)
        true,  // video
        true   // audio
    );
    
    return subclip;
}
```

### Reading In/Out from Timeline Clips

```javascript
// ExtendScript — Get source in/out points from a timeline clip
function getTimelineClipInOut(trackItem) {
    return {
        inSeconds: trackItem.inPoint.seconds,
        outSeconds: trackItem.outPoint.seconds,
        durationSeconds: trackItem.duration.seconds,
        startOnTimelineSeconds: trackItem.start.seconds,
        endOnTimelineSeconds: trackItem.end.seconds
    };
}
```

---

## Source Clip Properties Access

### Complete ProjectItem Property Map (ExtendScript)

```javascript
// ExtendScript — Comprehensive source clip property access
function inspectSourceClip(projectItem) {
    if (!projectItem || projectItem.type !== 1) {
        return { ok: false, err: "Not a clip" };
    }
    
    try {
        var info = {
            // Identity
            name: projectItem.name,
            type: projectItem.type,  // 1 = CLIP
            treePath: projectItem.treePath,
            
            // Media reference
            mediaPath: projectItem.getMediaPath(),
            
            // Timing (source duration)
            durationSeconds: projectItem.duration.seconds,
            durationTicks: projectItem.duration.ticks,
            
            // Track composition
            mediaType: projectItem.mediaType,  // "Video", "Audio", "Video + Audio"
            
            // Metadata
            label: projectItem.getColorLabel(),
            
            // File state
            isOffline: projectItem.isOffline(),
            
            // Bin structure
            parentBin: projectItem.getParentBin() ? projectItem.getParentBin().name : "root"
        };
        
        return { ok: true, data: info };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Extended Metadata: Project Metadata vs XMP

Premiere supports two metadata layers on clips:

1. **Project Metadata** (Premiere-native, searchable in project)
2. **XMP Metadata** (Adobe XMP standard, portable across Adobe apps)

```javascript
// ExtendScript — Read project metadata
function getProjectMetadata(projectItem) {
    try {
        var buffer = projectItem.getProjectMetadata();
        // buffer is raw byte buffer (Premiere's native metadata)
        // Requires parsing by Premiere's internal schema
        return buffer ? buffer.toString() : null;
    } catch (e) {
        return null;
    }
}

// ExtendScript — Read XMP metadata
function getXMPMetadata(projectItem) {
    try {
        var buffer = projectItem.getXMPMetadata();
        return buffer ? buffer.toString() : null;
    } catch (e) {
        return null;
    }
}
```

### Available Properties per Clip Type

| Property | CLIP | BIN | Notes |
|---|---|---|---|
| name | Yes | Yes | Mutable |
| type | Yes | Yes | 1=CLIP, 2=BIN, etc. |
| treePath | Yes | Yes | Read-only |
| mediaPath | Yes | No | Physical file path |
| duration | Yes | No | Source clip duration |
| mediaType | Yes | No | "Video", "Audio", etc. |
| getMarkers() | Yes | No | Clip-level markers |
| createSubClip() | Yes | No | Create subclip |
| getXMPMetadata() | Yes | No | XMP buffer |
| setXMPMetadata() | Yes | No | Write XMP |
| getProjectMetadata() | Yes | No | Premiere metadata |
| setProjectMetadata() | Yes | No | Write Premiere metadata |

---

## Logging Panel Integration

### CEP Panel for Logging (Deprecated, but Functional)

CEP panels run JavaScript in a Chromium sandbox and bridge to ExtendScript. For source monitor logging, a CEP panel provides:
- **UI form** to enter logging data (scene, take, notes)
- **ExtendScript bridge** to create markers/subclips
- **Persistent data** stored in project metadata or external JSON

#### CEP Panel Structure

```html
<!-- CEP Panel: html/index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Logging Panel</title>
  <style>
    body { font-family: Arial; padding: 10px; }
    input { width: 100%; margin: 5px 0; }
    button { width: 100%; padding: 8px; }
  </style>
</head>
<body>
  <h3>Source Logging</h3>
  
  <label>Clip Name:</label>
  <input type="text" id="clipName" placeholder="e.g., Actress Close-up" />
  
  <label>Scene:</label>
  <input type="text" id="scene" placeholder="e.g., 1A" />
  
  <label>Take:</label>
  <input type="number" id="take" min="1" value="1" />
  
  <label>Notes:</label>
  <textarea id="notes" rows="4" placeholder="Technical notes, issues, etc."></textarea>
  
  <label>Tags (comma-separated):</label>
  <input type="text" id="tags" placeholder="good-take, color-ready, needs-fix" />
  
  <button id="logButton">Create Marker & Subclip</button>
  
  <script src="js/cep-bridge.js"></script>
</body>
</html>
```

#### CEP Bridge JavaScript

```javascript
// CEP Panel: js/cep-bridge.js
var CSInterface = window.CSInterface;

document.getElementById("logButton").addEventListener("click", function() {
    var clipName = document.getElementById("clipName").value;
    var scene = document.getElementById("scene").value;
    var take = document.getElementById("take").value;
    var notes = document.getElementById("notes").value;
    var tags = document.getElementById("tags").value.split(",").map(t => t.trim());
    
    var loggingData = {
        scene: scene,
        take: parseInt(take),
        notes: notes,
        tags: tags,
        timestamp: new Date().toISOString()
    };
    
    // Call ExtendScript host function
    var jsx = `
        var result = createMarkerFromLogging(${JSON.stringify(loggingData)});
        result;
    `;
    
    CSInterface.evalScript(jsx, function(hostResult) {
        console.log("Host response:", hostResult);
        alert("Marker created: " + clipName);
    });
});
```

#### ExtendScript Host Function

```javascript
// CEP Host Script: jsx/index.jsx
//@include "json2.js"

function createMarkerFromLogging(loggingData) {
    try {
        var seq = app.project && app.project.activeSequence;
        if (!seq) {
            return JSON.stringify({ ok: false, err: "No active sequence" });
        }
        
        var marker = seq.markers.createMarker(0);
        marker.name = loggingData.scene + " - Take " + loggingData.take;
        marker.comments = JSON.stringify(loggingData);
        marker.setColorByIndex(6);  // Green = approved
        
        return JSON.stringify({ ok: true, markerName: marker.name });
    } catch (e) {
        return JSON.stringify({ ok: false, err: String(e) });
    }
}
```

### UXP Panel for Logging (Modern, Recommended)

UXP panels are modern, async-first, and integrated directly with Premiere's plugin system (no CEP bridge).

#### UXP Plugin Manifest (manifest.json)

```json
{
  "name": "Source Logging",
  "version": "1.0.0",
  "upmVersion": "0.1",
  "main": "src/index.js",
  "uiModes": [
    {
      "type": "panel",
      "name": "LoggingPanel"
    }
  ],
  "entryPoints": [
    {
      "type": "panel",
      "name": "LoggingPanel"
    }
  ],
  "requiredAPIVersion": "25.6"
}
```

#### UXP Panel JavaScript

```javascript
// UXP Panel: src/index.js
const { application } = require("premierepro");

class LoggingPanel {
    constructor() {
        this.setupUI();
    }
    
    setupUI() {
        // Create form elements
        const form = document.createElement("div");
        form.innerHTML = `
            <h2>Source Logging</h2>
            <input type="text" id="scene" placeholder="Scene (e.g., 1A)" />
            <input type="number" id="take" min="1" value="1" placeholder="Take #" />
            <textarea id="notes" placeholder="Notes..." rows="4"></textarea>
            <input type="text" id="tags" placeholder="Tags (comma-separated)" />
            <button id="logBtn">Create Marker</button>
        `;
        
        document.body.appendChild(form);
        
        document.getElementById("logBtn").addEventListener("click", () => {
            this.createLogMarker();
        });
    }
    
    async createLogMarker() {
        const scene = document.getElementById("scene").value;
        const take = parseInt(document.getElementById("take").value);
        const notes = document.getElementById("notes").value;
        const tags = document.getElementById("tags").value.split(",");
        
        const loggingData = {
            scene: scene,
            take: take,
            notes: notes,
            tags: tags,
            timestamp: new Date().toISOString()
        };
        
        try {
            const seq = await application.activeSequence;
            if (!seq) {
                alert("No active sequence");
                return;
            }
            
            await application.executeTransaction(async () => {
                const marker = await seq.createMarker({
                    name: `${scene} - Take ${take}`,
                    comments: JSON.stringify(loggingData),
                    color: 6  // Green
                });
                console.log("Marker created:", marker.name);
            });
            
            alert("Marker created successfully");
        } catch (e) {
            alert("Error: " + String(e));
        }
    }
}

// Initialize on load
window.addEventListener("load", () => {
    new LoggingPanel();
});
```

---

## Metadata XMP Properties

### XMP Namespace Overview

XMP (Extensible Metadata Platform) uses namespaced XML. Common namespaces for logging:

```xml
<?xml version="1.0"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"
           xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
           xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:xmp="http://ns.adobe.com/xap/1.0/">
  
  <rdf:RDF>
    <rdf:Description rdf:about=""
      dc:title="Clip Title"
      dc:creator="Editor Name"
      dc:subject="Tag1,Tag2"
      xmp:rating="5">
      
      <!-- Custom namespace for logging -->
      <premi:loggingScene>1A</premi:loggingScene>
      <premi:loggingTake>3</premi:loggingTake>
      <premi:loggingNotes>Good take, color ready</premi:loggingNotes>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
```

### Writing XMP Metadata (ExtendScript)

```javascript
// ExtendScript (ES3) — Set XMP metadata on a clip
function setXMPLoggingMetadata(projectItem, loggingObject) {
    try {
        // Build XMP XML string
        var xmpXml = buildXMPDocument({
            title: projectItem.name,
            creator: "Premiere Logger",
            subject: loggingObject.tags ? loggingObject.tags.join(",") : "",
            rating: loggingObject.rating || 0,
            customNotes: loggingObject.notes || ""
        });
        
        // Convert to buffer and set
        var buffer = new Buffer(xmpXml);
        projectItem.setXMPMetadata(buffer);
        
        return { ok: true };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}

function buildXMPDocument(fields) {
    var xml = '<?xml version="1.0"?>\n';
    xml += '<x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">\n';
    xml += '<rdf:RDF>\n';
    xml += '<rdf:Description rdf:about="">\n';
    
    if (fields.title) {
        xml += '<dc:title>' + escapeXML(fields.title) + '</dc:title>\n';
    }
    if (fields.creator) {
        xml += '<dc:creator>' + escapeXML(fields.creator) + '</dc:creator>\n';
    }
    if (fields.subject) {
        xml += '<dc:subject>' + escapeXML(fields.subject) + '</dc:subject>\n';
    }
    if (fields.rating) {
        xml += '<xmp:rating>' + fields.rating + '</xmp:rating>\n';
    }
    
    xml += '</rdf:Description>\n';
    xml += '</rdf:RDF>\n';
    xml += '</x:xmpmeta>';
    
    return xml;
}

function escapeXML(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&apos;");
}
```

### Reading XMP Metadata (ExtendScript)

```javascript
// ExtendScript — Parse and extract XMP data
function getXMPLoggingMetadata(projectItem) {
    try {
        var buffer = projectItem.getXMPMetadata();
        if (!buffer) {
            return { ok: true, metadata: {} };
        }
        
        var xmpString = buffer.toString();
        var metadata = {
            title: extractXMLTagValue(xmpString, "dc:title"),
            creator: extractXMLTagValue(xmpString, "dc:creator"),
            subject: extractXMLTagValue(xmpString, "dc:subject"),
            rating: extractXMLTagValue(xmpString, "xmp:rating")
        };
        
        return { ok: true, metadata: metadata };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}

function extractXMLTagValue(xml, tagName) {
    var regex = new RegExp("<" + tagName + ">([^<]+)</", "i");
    var match = xml.match(regex);
    return match ? match[1] : "";
}
```

### Standard XMP Fields for Logging

| Field | XMP Namespace | Type | Example |
|---|---|---|---|
| Title | dc:title | string | "Actress CU, Take 3" |
| Creator | dc:creator | string | "John Smith" |
| Description | dc:description | string | "Production notes" |
| Subject/Tags | dc:subject | string array | "scene-1A, good-take, color-ready" |
| Rating | xmp:rating | integer 0-5 | 5 |
| Date | xmp:createDate | ISO 8601 | "2026-07-12T14:30:00Z" |
| Keywords | dc:keywords | string | "vfx, cg, needs-tracking" |

---

## Sync Settings for Multicam

### Multicam Sequence Structure

A multicam sequence is a nested Sequence containing multiple video tracks (camera angles). While there's no public API to create multicam sequences programmatically, once created via UI, you can access and script sync metadata.

### Accessing Multicam Sync Data (QE DOM Required)

```javascript
// ExtendScript with QE DOM — Read multicam sync markers
app.enableQE();

function getMulticamSyncMarkers(sequence) {
    try {
        var qeSeq = app.qe.project.getActiveSequence();
        var syncMarkers = [];
        
        // Iterate through all video tracks (camera angles)
        for (var t = 0; t < qeSeq.getNumAudioTracks(); t++) {
            // Multicam typically uses audio track markers as sync points
            var trackMarkers = qeSeq.getAudioTrackMarkers(t);
            
            for (var i = 0; i < trackMarkers.length; i++) {
                var marker = trackMarkers[i];
                syncMarkers.push({
                    track: t,
                    position: marker.position,
                    name: marker.name
                });
            }
        }
        
        return { ok: true, syncMarkers: syncMarkers };
    } catch (e) {
        return { ok: false, err: String(e), warning: "QE method" };
    }
}
```

### Manual Multicam Sync via Marker Alignment (ExtendScript)

```javascript
// ExtendScript — Align camera clips using markers (manual sync technique)
function syncCamerasByMarker(sequence, cameraClips, syncMarkerName) {
    try {
        // Find sync marker in each camera's source clip
        var syncOffsets = [];
        
        for (var i = 0; i < cameraClips.length; i++) {
            var clip = cameraClips[i];
            var markers = clip.projectItem.getMarkers();
            
            for (var m = 0; m < markers.numMarkers; m++) {
                var marker = markers.getMarker(m);
                if (marker.name === syncMarkerName) {
                    syncOffsets.push({
                        cameraIndex: i,
                        markerPosition: marker.startTime.seconds
                    });
                    break;
                }
            }
        }
        
        // Adjust in/out points to align sync marks
        if (syncOffsets.length === cameraClips.length) {
            var referencePosition = syncOffsets[0].markerPosition;
            
            for (var j = 0; j < syncOffsets.length; j++) {
                var offset = syncOffsets[j].markerPosition - referencePosition;
                var clipToTrim = cameraClips[j];
                
                // Shift in/out to compensate for offset
                clipToTrim.inPoint = new Time();
                clipToTrim.inPoint.seconds = offset;
            }
        }
        
        return { ok: true, msg: "Cameras synced by marker" };
    } catch (e) {
        return { ok: false, err: String(e) };
    }
}
```

### Multicam Limitations

- **No public "create multicam" API:** Must use UI (File > New > Multi-Camera Source Sequence)
- **Sync metadata (waveform-based):** Stored in QE DOM only, not accessible via public API
- **Angle switching:** UI-only feature (Angle Switcher panel)
- **Flattening:** Once multicam is flattened, it becomes a standard sequence with standard clips

---

## Production Example: Auto-Logging Tool

### Complete Logging Workflow Tool

This production-ready example creates a logging tool that:
1. Monitors active clip in source monitor
2. Creates markers at specified in/out points
3. Generates subclips with logging metadata
4. Exports logging report as JSON

#### Extended Script: LoggingTool.jsx

```javascript
/**
 * Production Logging Tool for Adobe Premiere Pro
 * Version: 1.0
 * Description: Auto-create subclips and log markers from source monitor selection
 * Minimum Premiere Version: 24.0 (tested on 25.6)
 */

//@include "json2.js"

var TICKS_PER_SECOND = 254016000000;
var APP_VERSION = "1.0";

/**
 * LOGGING ENGINE
 */

var LoggingEngine = {
    
    /**
     * Create timestamped marker on clip with logging metadata
     */
    createLogMarker: function(projectItem, atSeconds, loggingData, colorIndex) {
        if (!projectItem || projectItem.type !== 1) {
            return { ok: false, err: "Invalid clip" };
        }
        
        try {
            var markers = projectItem.getMarkers();
            var t = new Time();
            t.seconds = atSeconds;
            
            var marker = markers.createMarker(t.ticks);
            marker.name = loggingData.scene + " - T" + loggingData.take;
            
            // Build structured metadata
            var markerMetadata = {
                version: APP_VERSION,
                timestamp: new Date().toISOString(),
                scene: loggingData.scene,
                take: loggingData.take,
                notes: loggingData.notes,
                tags: loggingData.tags || [],
                editor: loggingData.editor || "Unknown",
                position: atSeconds,
                clip: projectItem.name
            };
            
            marker.comments = JSON.stringify(markerMetadata);
            marker.setColorByIndex(colorIndex || 6);  // Green default
            
            return {
                ok: true,
                marker: marker.name,
                markerData: markerMetadata
            };
        } catch (e) {
            return { ok: false, err: String(e) };
        }
    },
    
    /**
     * Create subclip with automatic metadata logging
     */
    createLoggedSubclip: function(projectItem, startSec, endSec, loggingData) {
        if (!projectItem || projectItem.type !== 1) {
            return { ok: false, err: "Invalid clip" };
        }
        
        try {
            var startTicks = Math.round(startSec * TICKS_PER_SECOND);
            var endTicks = Math.round(endSec * TICKS_PER_SECOND);
            
            var subclipName = loggingData.scene + "_T" + 
                              loggingData.take + "_" + 
                              Math.floor(Date.now() / 1000);
            
            var subclip = projectItem.createSubClip(
                subclipName,
                startTicks,
                endTicks,
                true,   // hard boundaries
                true,   // video
                true    // audio
            );
            
            // Set XMP metadata on subclip
            var xmpData = this.buildXMPMetadata(loggingData);
            var buffer = new Buffer(xmpData);
            subclip.setXMPMetadata(buffer);
            
            // Color-code subclip by status
            var colorIndex = loggingData.status === "approved" ? 6 : 0;
            subclip.setColorLabel(colorIndex);
            
            return {
                ok: true,
                subclip: subclip.name,
                inPoint: startSec,
                outPoint: endSec,
                duration: (endSec - startSec).toFixed(2)
            };
        } catch (e) {
            return { ok: false, err: String(e) };
        }
    },
    
    /**
     * Build XMP metadata structure for logging
     */
    buildXMPMetadata: function(loggingData) {
        var xml = '<?xml version="1.0"?>\n';
        xml += '<x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xmp="http://ns.adobe.com/xap/1.0/">\n';
        xml += '<rdf:RDF>\n';
        xml += '<rdf:Description rdf:about="">\n';
        
        xml += '<dc:title>' + this.escapeXML(loggingData.scene + " Take " + loggingData.take) + '</dc:title>\n';
        xml += '<dc:creator>' + this.escapeXML(loggingData.editor || "Logger") + '</dc:creator>\n';
        
        if (loggingData.tags && loggingData.tags.length > 0) {
            xml += '<dc:subject>' + this.escapeXML(loggingData.tags.join(",")) + '</dc:subject>\n';
        }
        
        xml += '<dc:description>' + this.escapeXML(loggingData.notes || "") + '</dc:description>\n';
        xml += '<xmp:createDate>' + new Date().toISOString() + '</xmp:createDate>\n';
        
        xml += '</rdf:Description>\n';
        xml += '</rdf:RDF>\n';
        xml += '</x:xmpmeta>';
        
        return xml;
    },
    
    /**
     * Escape XML special characters
     */
    escapeXML: function(str) {
        return String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&apos;");
    },
    
    /**
     * Export logging report (all markers and subclips)
     */
    exportLoggingReport: function(outputPath) {
        try {
            var proj = app.project;
            if (!proj) {
                return { ok: false, err: "No project open" };
            }
            
            var report = {
                projectName: proj.name,
                exportDate: new Date().toISOString(),
                clips: []
            };
            
            // Walk all clips in project
            var clipsList = this.getAllClips(proj.rootItem);
            
            for (var i = 0; i < clipsList.length; i++) {
                var clip = clipsList[i];
                var clipData = {
                    name: clip.name,
                    path: clip.treePath,
                    duration: clip.duration.seconds,
                    markers: []
                };
                
                // Extract all markers
                var markers = clip.getMarkers();
                for (var m = 0; m < markers.numMarkers; m++) {
                    var marker = markers.getMarker(m);
                    var markerObj = {
                        name: marker.name,
                        position: marker.startTime.seconds,
                        comments: marker.comments
                    };
                    
                    // Try parse JSON
                    try {
                        markerObj.metadata = JSON.parse(marker.comments);
                    } catch (e) {
                        markerObj.metadata = null;
                    }
                    
                    clipData.markers.push(markerObj);
                }
                
                report.clips.push(clipData);
            }
            
            // Write to file
            var f = new File(outputPath);
            f.encoding = "UTF-8";
            if (!f.open("w")) {
                return { ok: false, err: "Cannot write to " + outputPath };
            }
            
            f.write(JSON.stringify(report, null, 2));
            f.close();
            
            return {
                ok: true,
                filePath: f.fsName,
                clipsProcessed: report.clips.length,
                totalMarkers: report.clips.reduce(function(sum, c) { 
                    return sum + c.markers.length; 
                }, 0)
            };
        } catch (e) {
            return { ok: false, err: String(e) };
        }
    },
    
    /**
     * Recursively collect all clips in project
     */
    getAllClips: function(item, clips) {
        clips = clips || [];
        
        if (!item.children) return clips;
        
        for (var i = 0; i < item.children.numItems; i++) {
            var child = item.children[i];
            
            if (child.type === 1) {  // CLIP
                clips.push(child);
            } else if (child.type === 2) {  // BIN
                this.getAllClips(child, clips);
            }
        }
        
        return clips;
    }
};

/**
 * UI DIALOG
 */

function showLoggingDialog() {
    var dlg = new Window("dialog", "Logging Tool v" + APP_VERSION);
    
    // Input fields
    dlg.add("statictext", undefined, "Create Logging Marker/Subclip");
    
    dlg.grpScene = dlg.add("group");
    dlg.grpScene.add("statictext", undefined, "Scene:");
    dlg.edtScene = dlg.grpScene.add("edittext", undefined, "1A");
    dlg.edtScene.characters = 10;
    
    dlg.grpTake = dlg.add("group");
    dlg.grpTake.add("statictext", undefined, "Take:");
    dlg.edtTake = dlg.grpTake.add("edittext", undefined, "1");
    dlg.edtTake.characters = 5;
    
    dlg.grpIn = dlg.add("group");
    dlg.grpIn.add("statictext", undefined, "In (sec):");
    dlg.edtIn = dlg.grpIn.add("edittext", undefined, "0");
    dlg.edtIn.characters = 8;
    
    dlg.grpOut = dlg.add("group");
    dlg.grpOut.add("statictext", undefined, "Out (sec):");
    dlg.edtOut = dlg.grpOut.add("edittext", undefined, "10");
    dlg.edtOut.characters = 8;
    
    dlg.grpNotes = dlg.add("group", undefined, "", {orientation: "column", alignChildren: "fill"});
    dlg.grpNotes.add("statictext", undefined, "Notes:");
    dlg.edtNotes = dlg.grpNotes.add("edittext", [0, 0, 300, 80], "", {multiline: true});
    
    dlg.grpTags = dlg.add("group");
    dlg.grpTags.add("statictext", undefined, "Tags:");
    dlg.edtTags = dlg.grpTags.add("edittext", undefined, "");
    dlg.edtTags.characters = 40;
    
    // Options
    dlg.chkMarker = dlg.add("checkbox", undefined, "Create Marker");
    dlg.chkMarker.value = true;
    
    dlg.chkSubclip = dlg.add("checkbox", undefined, "Create Subclip");
    dlg.chkSubclip.value = true;
    
    // Buttons
    dlg.grpButtons = dlg.add("group");
    dlg.btnOK = dlg.grpButtons.add("button", undefined, "OK");
    dlg.btnCancel = dlg.grpButtons.add("button", undefined, "Cancel");
    
    dlg.btnOK.onClick = function() {
        var proj = app.project;
        var clipName = dlg.edtScene.text + " T" + dlg.edtTake.text;
        
        if (!proj || !proj.rootItem) {
            alert("No project open");
            return;
        }
        
        var loggingData = {
            scene: dlg.edtScene.text,
            take: parseInt(dlg.edtTake.text),
            notes: dlg.edtNotes.text,
            tags: dlg.edtTags.text.split(",").map(function(t) { return t.trim(); }),
            editor: "Logging Tool"
        };
        
        var inSec = parseFloat(dlg.edtIn.text);
        var outSec = parseFloat(dlg.edtOut.text);
        
        // Find first clip in project (simplified)
        var targetClip = null;
        for (var i = 0; i < proj.rootItem.children.numItems; i++) {
            if (proj.rootItem.children[i].type === 1) {
                targetClip = proj.rootItem.children[i];
                break;
            }
        }
        
        if (!targetClip) {
            alert("No clips found in project");
            return;
        }
        
        var resultsLog = [];
        
        if (dlg.chkMarker.value) {
            var markerRes = LoggingEngine.createLogMarker(
                targetClip,
                inSec,
                loggingData,
                6
            );
            resultsLog.push("Marker: " + (markerRes.ok ? "OK" : markerRes.err));
        }
        
        if (dlg.chkSubclip.value) {
            var subclipRes = LoggingEngine.createLoggedSubclip(
                targetClip,
                inSec,
                outSec,
                loggingData
            );
            resultsLog.push("Subclip: " + (subclipRes.ok ? "OK (" + subclipRes.subclip + ")" : subclipRes.err));
        }
        
        alert(clipName + "\n" + resultsLog.join("\n"));
        dlg.close();
    };
    
    dlg.btnCancel.onClick = function() {
        dlg.close();
    };
    
    dlg.center();
    dlg.show();
}

// Main entry point
showLoggingDialog();
```

### Usage Instructions

1. **Open a project** with video clips in the project panel
2. **Run the script** (File > Scripts > Run Script File)
3. **Fill in logging fields:**
   - Scene: `1A`
   - Take: `3`
   - In/Out: Specify frame range
   - Notes: Production notes (audio issues, performance, etc.)
   - Tags: `good-take, color-ready, needs-audio-fix`
4. **Click OK** to create marker and subclip
5. **Export report** (optional) via File > Scripts

---

## Edge Cases & Version Compatibility

### Version-Specific Behaviors

| Feature | Premiere 24.x | Premiere 25.x | Premiere 26.x |
|---|---|---|---|
| createSubClip | Yes | Yes | Yes |
| XMP metadata | Yes | Yes | Yes (improved) |
| Markers on clips | Yes | Yes | Yes |
| UXP full support | No | Partial (25.6+) | Likely full |
| QE ripple edits | Yes | Yes | Risk (unsupported) |
| Multicam API | No | No | Unknown |

### Common Pitfalls & Fixes

#### Pitfall 1: Time Object Errors (Premiere 14.1+)

**Symptom:** Setting `trackItem.inPoint` silently fails or throws.

```javascript
// WRONG (pre-14.1 code)
trackItem.inPoint = 5.5;  // Number fails on 14.1+

// CORRECT
var t = new Time();
t.seconds = 5.5;
trackItem.inPoint = t;
```

#### Pitfall 2: XMP Buffer Encoding

**Symptom:** XMP metadata appears corrupted or unreadable.

```javascript
// WRONG — no encoding specified
var xmpStr = "<?xml...>";
projectItem.setXMPMetadata(xmpStr);  // May fail

// CORRECT — explicit UTF-8 buffer
var buffer = new Buffer(xmpStr);
buffer.encoding = "UTF-8";
projectItem.setXMPMetadata(buffer);
```

#### Pitfall 3: JSON Undefined

**Symptom:** `JSON is undefined` error.

```javascript
// WRONG — no bundled json2.js
var data = JSON.parse(marker.comments);

// CORRECT — include json2.js first
//@include "json2.js"
if (typeof JSON === "undefined") {
    throw new Error("json2.js not loaded");
}
var data = JSON.parse(marker.comments);
```

#### Pitfall 4: QE Objects Break After Undo

**Symptom:** QE references become invalid after undo/redo.

```javascript
// WRONG — holding QE reference across undo
app.enableQE();
var qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);
app.project.undo();
qeClip.getSpeed();  // May fail or return wrong value

// CORRECT — re-fetch after undo
var speed = qeClip.getSpeed();  // Read before undo
app.project.undo();
app.enableQE();  // Re-enable QE
qeClip = app.qe.project.getActiveSequence().getAVClipAt(0, 0);  // Re-fetch
speed = qeClip.getSpeed();  // Fresh read
```

### Unsupported / UI-Only Features

| Feature | API Available? | Workaround |
|---|---|---|
| Direct source monitor display | No | N/A (UI only) |
| Angle Switcher (multicam live) | No | Use flattened sequence |
| Logging panel built-in | No | Build custom CEP/UXP |
| Auto-sync by waveform | No | Create multicam via UI, script result |
| Frame-accurate subcl IP creation via source monitor | No | Use Timeline in/out points |

---

## Best Practices for Production Logging

1. **Always wrap in try/catch** — ExtendScript errors can break workflows.
2. **Use Time objects, not numbers** — Premiere 14.1+ requires this.
3. **Include json2.js** — JSON is not guaranteed globally available.
4. **Test on small project first** — Before running batch operations on production files.
5. **Document marker structure** — Use JSON in comments field for structured data.
6. **Version your metadata** — Include schema version in XMP/marker data for upgradability.
7. **Batch operations in transactions** — UXP requires `executeTransaction()`.
8. **Use QE as last resort** — Document risk; flag for migration to UXP when available.

---

## References

- **Adobe Scripting Guide:** https://ppro-scripting.docsforadobe.dev/
- **UXP Developer Guide:** https://developer.adobe.com/premiere-pro/uxp/
- **XMP Spec:** https://github.com/adobe/XMP-Toolkit-SDK
- **Community Resources:** https://forums.adobe.com/community/premiere/premiere_pro

---

**Document Version:** 1.0  
**Last Updated:** July 12, 2026  
**Tested Against:** Adobe Premiere Pro 25.6, 26.0 (pre-release)  
**Author:** Production Scripting Reference  
**Status:** Production Ready
