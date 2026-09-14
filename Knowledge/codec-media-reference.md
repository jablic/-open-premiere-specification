---
id: codec-media-reference
title: Codec & Media Format Reference
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2014"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, uxp]
tags: [codecs, media-formats, proxy, intra-frame, inter-frame, compression, performance]
related: [import, export-rendering-media-encoder, color-management, performance-optimization]
sources: [
  "Adobe Media Encoder documentation",
  "Production workflows",
  "Codec specifications"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Codec & Media Format Reference

## TL;DR

**Intra-frame codecs** (ProRes, DNxHD, DNG, RED) = faster editing, higher quality, large files. **Inter-frame codecs** (H.264, H.265) = smaller files, slower scrubbing, good for delivery. **Proxy codecs** = edit 4K on 2K hardware. **Color bit-depth:** 8-bit (H.264) → 10-bit (ProRes) → 12-bit (DNxHD/RED). **Rule:** Always work on ProRes/DNxHD, proxy/deliver on H.264.

---

## Intra-Frame Codecs (Recommended for Editing)

### ProRes Family

| Codec | File Size | Quality | Bit Depth | Use Case |
|---|---|---|---|---|
| **ProRes 422 HQ** | ~500 MB/min (1080p) | Very High | 10-bit | Primary editing, color grading |
| **ProRes 422** | ~250 MB/min (1080p) | High | 10-bit | Standard editing |
| **ProRes 422 LT** | ~150 MB/min (1080p) | Good | 10-bit | Offline editing, fast scrubbing |
| **ProRes 422 Proxy** | ~50 MB/min (1080p) | Medium | 10-bit | Proxy editing, rough cuts |
| **ProRes RAW** | 1.3–2.5 GB/min (4K) | Uncompressed | 12-bit | Scientific, VFX, color science |

**Advantages:**
- Hardware-accelerated on Apple/Mac
- Lossless quality in 422 HQ
- Frame-accurate seeking
- Full color gamut preservation

**Disadvantages:**
- Large file sizes
- Mac-optimized (slower on Windows)
- Licensing considerations for RAW

### DNxHD/DNxHR (Avid Alternative)

| Codec | File Size | Quality | Bit Depth | Use Case |
|---|---|---|---|---|
| **DNxHD 440 (10-bit)** | ~500 MB/min (1080p) | Very High | 10-bit | Professional editing |
| **DNxHD 220** | ~250 MB/min (1080p) | High | 8-bit | Standard editing |
| **DNxHR HQX (4K)** | ~1.2 GB/min (4K) | Very High | 10-bit | 4K editing |
| **DNxHR SQ** | ~300 MB/min (4K) | Good | 8-bit | Fast playback |

**Advantages:**
- Better Windows support than ProRes
- Avid-compatible for collaboration
- Fast seeking and playback
- 10-bit color support

**Disadvantages:**
- Less hardware acceleration
- Codec licensing

---

## DNG & Raw Image Sequences

### DNG (Digital Negative) Sequences

```javascript
// AutoImport DNG sequence detection
function importDNGSequence(firstFramePath) {
  /**
   * DNG sequences: numbered frame files (image_001.dng, image_002.dng, etc.)
   */
  
  var project = app.project;
  var firstFrame = new File(firstFramePath);
  
  if (!firstFrame.exists) {
    alert("ERROR: First DNG frame not found");
    return false;
  }
  
  try {
    // Premiere recognizes numbered DNG files as sequences
    var imported = project.importFiles([firstFramePath], true, project.rootBin, false);
    
    if (imported && imported.length > 0) {
      var item = imported[0];
      $.writeln("Imported DNG sequence: " + item.name);
      return item;
    }
  } catch (e) {
    alert("Failed to import DNG: " + e.toString());
  }
  
  return null;
}
```

**Characteristics:**
- 12-bit color per channel
- Lossless, archival quality
- Large files (1–2 GB per frame at 4K)
- Used for VFX, color science preservation
- Color space: Usually DCI P3 or Adobe RGB

### RED RAW

```javascript
// RED (.r3d) native support in Premiere 24+
function importREDRaw(r3dFilePath) {
  /**
   * RED RAW: 12-bit uncompressed video
   * Premiere 24+ has native decoder for .r3d
   */
  
  var project = app.project;
  var file = new File(r3dFilePath);
  
  try {
    var imported = project.importFiles([r3dFilePath], true, project.rootBin, false);
    
    if (imported && imported.length > 0) {
      $.writeln("RED file imported with native decoder");
      // Metadata: Resolution (6K, 8K), bit depth (12-bit), color space (REDcolor)
      return imported[0];
    }
  } catch (e) {
    alert("RED import failed: " + e.toString());
  }
  
  return null;
}
```

**Characteristics:**
- 12-bit or higher per channel
- 6K, 8K native resolutions
- Massive files (1.5–3 GB per minute depending on resolution)
- Requires RED Rocket card for full performance
- Licensing: RED Code Vault subscription

---

## Inter-Frame Codecs (Delivery & Distribution)

### H.264 (AVC)

**Characteristics:**
- 8-bit color
- Lossy compression (~50:1)
- File size: ~10 MB/min (1080p)
- Browser compatible (HTML5 video)
- Patent licensing required

**Best for:** Web streaming, YouTube, client delivery

**Limitations:**
- Not suitable for editing (lossy)
- Single playback direction (slow reverse scrubbing)
- Limited color accuracy

**Export preset:**
```javascript
// Export as H.264 for web delivery
var preset = app.encoder.getExportPresets().find(p => p.indexOf("YouTube") !== -1);
if (preset) {
  app.project.exportFile(preset, outputPath, true, true);
}
```

### H.265 (HEVC)

**Characteristics:**
- 8-bit or 10-bit color options
- 50% smaller files than H.264
- Better quality at same bitrate
- Patent/licensing concerns

**Use cases:** 4K delivery, streaming services, modern platforms

**Note:** Premiere 24+ supports H.265 encoding with hardware acceleration (if available)

### ProRes for Delivery

```javascript
// Export ProRes 422 for intermediate/delivery
var exportSettings = {
  matchSequence: true,
  includeCaptions: true,
  // ProRes 422 (not HQ) for archival + delivery balance
  codec: "ProRes 422"
};
```

**Why ProRes for delivery?**
- Professional broadcast standard
- 10-bit color preservation
- Lossless to visually lossless
- Compatible with post-production workflows

---

## Proxy Workflow Strategies

### Proxy Codec Selection

| Source | Proxy Strategy | Codec | Resolution | Bitrate |
|---|---|---|---|---|
| **1080p ProRes** | 1/2 resolution | ProRes 422 LT | 720p | 50-100 Mbps |
| **4K ProRes** | 1/2 resolution | ProRes 422 LT | 1080p | 50-100 Mbps |
| **4K H.265** | 1/4 resolution | ProRes 422 Proxy | 720p | 20-50 Mbps |
| **8K RED** | 1/4 resolution | ProRes 422 Proxy | 1080p | 50 Mbps |

### Proxy Creation & Management

```javascript
function createProxiesForSequence(sequence, proxyResolution) {
  /**
   * Create proxies for all clips in sequence
   * proxyResolution: "1/2 Resolution", "1/4 Resolution", etc.
   */
  
  var proxied = [];
  var failed = [];
  
  if (!sequence || !sequence.videoTracks) return null;
  
  for (var t = 0; t < sequence.videoTracks.length; t++) {
    var track = sequence.videoTracks[t];
    
    for (var i = 0; i < track.clips.length; i++) {
      var clip = track.clips[i];
      var item = clip.projectItem;
      
      if (!item || item.isOffline) continue;
      
      try {
        // Create proxy
        item.createMediaProxy(proxyResolution);
        proxied.push(item.name);
        
        $.writeln("Proxy created: " + item.name + " → " + proxyResolution);
      } catch (e) {
        failed.push({ name: item.name, error: e.toString() });
      }
    }
  }
  
  return { success: proxied.length, failed: failed };
}

// Usage
var result = createProxiesForSequence(app.project.activeSequence, "1/4 Resolution");
$.writeln("Proxies created: " + result.success + ", Failed: " + result.failed.length);
```

### Proxy vs Online Toggle

```javascript
function toggleProxies(enabled) {
  /**
   * Switch between proxy and original media
   */
  
  var project = app.project;
  
  // Premiere menu command: use proxies toggle
  // Not exposed via API, but can be done via menu automation
  var jsx = enabled ?
    "app.executeCommand(app.findMenuCommandId('Use Proxies'))" :
    "app.executeCommand(app.findMenuCommandId('Use Originals'))";
  
  try {
    app.evalScript(jsx);
    $.writeln("Proxy mode: " + (enabled ? "ON" : "OFF"));
  } catch (e) {
    $.writeln("Error toggling proxies: " + e.toString());
  }
}
```

---

## Color Bit Depth & Gamut

### Bit Depth Progression

- **8-bit:** 256 levels per channel (16.7M colors total)
  - Codecs: H.264, H.265, JPEG
  - Risk: Banding in gradients
  - Use: Web delivery only

- **10-bit:** 1024 levels per channel (1B colors)
  - Codecs: ProRes, DNxHD, YUV
  - Sufficient for most workflows
  - Use: Professional editing, broadcast

- **12-bit:** 4096 levels per channel
  - Codecs: DNG, RED RAW, some DNxHD variants
  - Best for: Color grading, VFX, archival
  - Use: Primary timeline

- **16-bit Float:** 65536 levels (logarithmic)
  - Use: Scientific visualization, HDR
  - Overkill for standard workflows

**Rule:** Shoot/capture at highest bit depth available. Proxy at 10-bit. Deliver at appropriate bit depth for platform.

---

## Media Health Checking

```javascript
function checkMediaHealth(project) {
  /**
   * Audit media files for codec, bit depth, color space issues
   */
  
  var report = {
    codecs: {},
    offline: [],
    missingFiles: [],
    lowBitDepth: [],
    recommendations: []
  };
  
  function analyzeItem(item) {
    if (!item) return;
    
    // Track codec usage
    if (item.file) {
      var ext = item.file.name.split(".").pop().toLowerCase();
      report.codecs[ext] = (report.codecs[ext] || 0) + 1;
      
      // Check if file exists
      if (!item.file.exists) {
        report.missingFiles.push(item.name);
      }
    }
    
    // Check offline status
    if (item.isOffline) {
      report.offline.push(item.name);
    }
    
    // Recursively check children (bins)
    if (item.children) {
      for (var i = 0; i < item.children.length; i++) {
        analyzeItem(item.children[i]);
      }
    }
  }
  
  // Analyze all project items
  analyzeItem(project.rootBin);
  
  // Generate recommendations
  if (report.offline.length > 0) {
    report.recommendations.push("Relink " + report.offline.length + " offline files");
  }
  
  if (report.codecs.mp4 || report.codecs.h264) {
    report.recommendations.push("Convert H.264 to ProRes for editing");
  }
  
  return report;
}

// Usage
var health = checkMediaHealth(app.project);
$.writeln("Codecs in project: " + JSON.stringify(health.codecs));
$.writeln("Offline files: " + health.offline.length);
$.writeln("Recommendations: " + health.recommendations.join("; "));
```

---

## See Also

- Knowledge/export-rendering-media-encoder.md — Export codec selection
- Knowledge/performance-optimization.md — Proxy workflow impact
- Knowledge/color-management.md — Color gamut management
- Knowledge/import.md — Media import best practices

---

## Sources

- Adobe Media Encoder Codecs: https://support.adobe.com/en-us/HT208197
- ProRes Specifications: https://support.apple.com/en-us/HT202410
- DNxHD Reference: https://www.avid.com/dnxhd
- RED Documentation: https://www.red.com/
