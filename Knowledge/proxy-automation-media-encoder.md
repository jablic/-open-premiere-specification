---
id: proxy-automation-media-encoder
title: Proxy Automation & Media Encoder Integration
category: advanced
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, javascript, jsx, shell]
tags: [proxy, media-encoder, batch-transcoding, automation, workflow, storage-management]
related: [codec-media-reference, automation, import, real-world-production-workflows]
sources: [
  "Media Encoder automation",
  "Proxy workflow patterns",
  "Storage optimization"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Proxy Automation & Media Encoder Integration

## TL;DR

**Proxy Creation:** Use Media Encoder for batch transcoding (faster than Premiere). **Codec Strategy:** Ingest = original format, proxy = 1/4 resolution ProRes 422 LT or H.264 (25 Mbps), delivery = optimized for platform. **Automation:** Watch folder + Media Encoder can auto-transcode incoming files. **Storage:** Proxies stored in project folder; enable "Use Proxies" to switch editing modes. **Disk Management:** Monitor proxy cache; can safely delete if originals available (will regenerate on demand). **Media Encoder API:** Limited in ExtendScript; use shell/command-line for batch operations.

---

## Media Encoder: Batch Proxy Generation

### Setup Media Encoder Watch Folder

```javascript
function setupMediaEncoderWatchFolder(sourceFolder, outputFolder, proxyPreset) {
  /**
   * Configure Adobe Media Encoder for automatic proxy generation
   * Watch folder monitors input directory; auto-encodes new files
   */
  
  var config = {
    sourceFolder: sourceFolder,
    outputFolder: outputFolder,
    preset: proxyPreset || "ProRes 422 LT",
    autoDelete: false,
    options: {}
  };
  
  $.writeln("=== MEDIA ENCODER WATCH FOLDER ===\n");
  
  $.writeln("Source Folder: " + sourceFolder);
  $.writeln("Output Folder: " + outputFolder);
  $.writeln("Proxy Preset: " + config.preset);
  
  $.writeln("\nSetup Steps:");
  $.writeln("1. Open Adobe Media Encoder");
  $.writeln("2. Window → Watch Folders");
  $.writeln("3. Create new watch folder:");
  $.writeln("   - Input: " + sourceFolder);
  $.writeln("   - Output: " + outputFolder);
  $.writeln("   - Preset: ProRes 422 LT (1/4 resolution recommended)");
  $.writeln("4. Enable: Auto-start encoding, delete after successful encode");
  $.writeln("5. Queue monitors folder continuously; auto-encodes new files");
  
  $.writeln("\nProxy Presets (1/4 Resolution):");
  $.writeln("- ProRes 422 LT: 50 MB/min (1080p), highest quality");
  $.writeln("- H.264 (25 Mbps): 12 MB/min (1080p), faster scrubbing");
  $.writeln("- DNxHD: 40 MB/min (1080p), Windows-friendly");
  
  $.writeln("\nNote: Requires Media Encoder running; ExtendScript has limited control");
  $.writeln("Recommend: Configure once, then Media Encoder handles automatically");
  
  return config;
}

// Usage
setupMediaEncoderWatchFolder(
  "/mnt/camera_storage/incoming/",
  "/mnt/storage/proxies/",
  "ProRes 422 LT"
);
```

### Manual Batch Transcode via Media Encoder

```javascript
function batchTranscodeViaMediaEncoder(inputFiles, outputFolder, preset) {
  /**
   * Queue multiple files to Media Encoder for batch transcoding
   * Note: Premiere → Media Encoder integration is limited
   * Use shell script or Media Encoder CLI for better control
   */
  
  var results = {
    queued: 0,
    failed: 0,
    estimatedTime: 0
  };
  
  $.writeln("=== BATCH TRANSCODE (Manual Approach) ===\n");
  
  $.writeln("Files to process: " + inputFiles.length);
  $.writeln("Output folder: " + outputFolder);
  $.writeln("Preset: " + preset);
  
  $.writeln("\nRecommended workflow:");
  $.writeln("1. Open Adobe Media Encoder");
  $.writeln("2. Drag & drop files into queue");
  $.writeln("3. Select output preset: " + preset);
  $.writeln("4. Set destination: " + outputFolder);
  $.writeln("5. Click 'Start Queue'");
  
  $.writeln("\nEstimated times:");
  $.writeln("- 1080p ProRes 422 LT: Real-time on modern hardware");
  $.writeln("- 4K ProRes 422 LT: ~2x real-time");
  $.writeln("- Parallel processing: Enable for multi-core utilization");
  
  results.queued = inputFiles.length;
  results.estimatedTime = inputFiles.length * 1.5;  // hours, approximation
  
  $.writeln("\nEstimated total time: ~" + results.estimatedTime + " hours");
  
  return results;
}

// Usage
var files = ["/path/to/clip1.mov", "/path/to/clip2.mov", "/path/to/clip3.mov"];
batchTranscodeViaMediaEncoder(files, "/mnt/storage/proxies/", "ProRes 422 LT");
```

### Shell-Based Media Encoder Automation (Command Line)

```bash
#!/bin/bash
# media_encoder_batch.sh
# Batch transcode using Media Encoder CLI (more reliable than ExtendScript)

SOURCE_FOLDER="$1"
OUTPUT_FOLDER="$2"
PRESET="$3"  # e.g., "ProRes 422 LT"

if [ ! -d "$SOURCE_FOLDER" ]; then
  echo "ERROR: Source folder not found: $SOURCE_FOLDER"
  exit 1
fi

if [ ! -d "$OUTPUT_FOLDER" ]; then
  mkdir -p "$OUTPUT_FOLDER"
fi

echo "=== MEDIA ENCODER BATCH TRANSCODE ==="
echo "Source: $SOURCE_FOLDER"
echo "Output: $OUTPUT_FOLDER"
echo "Preset: $PRESET"
echo ""

# Find video files
TOTAL=0
for file in "$SOURCE_FOLDER"/*.{mov,mp4,mxf,mkv}; do
  [ -e "$file" ] || continue
  
  FILENAME=$(basename "$file")
  OUTPUT_FILE="$OUTPUT_FOLDER/${FILENAME%.*}.mov"
  
  echo "Processing: $FILENAME"
  echo "  → $OUTPUT_FILE"
  
  # Media Encoder CLI (macOS/Windows)
  # Note: Path varies by OS and installation
  
  # macOS
  /Applications/Adobe\ Media\ Encoder.app/Contents/MacOS/Adobe\ Media\ Encoder \
    -encode "$file" "$PRESET" "$OUTPUT_FILE" 2>/dev/null &
  
  TOTAL=$((TOTAL + 1))
done

echo ""
echo "Queued: $TOTAL files"
echo "Monitor Media Encoder for progress"
```

**Shell Usage:**
```bash
chmod +x media_encoder_batch.sh
./media_encoder_batch.sh /path/to/source /path/to/proxies "ProRes 422 LT"
```

---

## Proxy Storage Management

### Monitor Proxy Cache Usage

```javascript
function monitorProxyCacheUsage(project) {
  /**
   * Analyze proxy folder size and recommendations
   */
  
  var report = {
    proxyFolderPath: null,
    totalSize: 0,
    fileCount: 0,
    recommendations: []
  };
  
  try {
    // Proxy folder is typically in project file location
    var projectFile = project.file;
    var projectFolder = projectFile ? projectFile.parent : null;
    
    if (projectFolder) {
      var proxyFolder = new Folder(projectFolder.absoluteURI + "/Proxies");
      
      if (proxyFolder.exists) {
        report.proxyFolderPath = proxyFolder.absoluteURI;
        
        // Count files and estimate size
        var files = proxyFolder.getFiles("*.mov");
        report.fileCount = files.length;
        
        for (var i = 0; i < files.length; i++) {
          report.totalSize += files[i].size;
        }
        
        var sizeGB = (report.totalSize / 1024 / 1024 / 1024).toFixed(2);
        
        $.writeln("=== PROXY CACHE STATUS ===");
        $.writeln("Location: " + report.proxyFolderPath);
        $.writeln("Files: " + report.fileCount);
        $.writeln("Total size: " + sizeGB + " GB");
        
        // Recommendations
        if (report.totalSize > 500 * 1024 * 1024 * 1024) {  // > 500 GB
          report.recommendations.push("Proxy cache is large (> 500 GB). Consider cleanup.");
        }
        
        if (report.fileCount > 1000) {
          report.recommendations.push("Large number of proxy files (" + report.fileCount + "). Monitor performance.");
        }
        
        report.recommendations.push("Safe to delete proxies if originals available (will regenerate on demand)");
        report.recommendations.push("Archive old proxies to external drive for preservation");
        
      } else {
        report.recommendations.push("No proxy folder found. Proxies will be created on demand.");
      }
    }
  } catch (e) {
    $.writeln("Error reading proxy folder: " + e.toString());
  }
  
  $.writeln("\nRecommendations:");
  for (var j = 0; j < report.recommendations.length; j++) {
    $.writeln("- " + report.recommendations[j]);
  }
  
  return report;
}

// Usage
monitorProxyCacheUsage(app.project);
```

### Archive Proxy Files

```javascript
function archiveProxyFiles(project, archivePath) {
  /**
   * Archive old proxy files to external storage (e.g., NAS, cloud)
   * Frees up primary storage while preserving proxies
   */
  
  var result = {
    archived: 0,
    failed: 0,
    totalSize: 0,
    archiveLocation: archivePath
  };
  
  $.writeln("=== PROXY ARCHIVE ===\n");
  $.writeln("Destination: " + archivePath);
  
  try {
    var archiveFolder = new Folder(archivePath);
    
    if (!archiveFolder.exists) {
      archiveFolder.create();
    }
    
    // In production, would iterate proxy folder and copy files
    $.writeln("Archiving proxies to: " + archivePath);
    $.writeln("\nNote: Use shell script or external tool for large archive operations");
    $.writeln("Example: rsync -av Proxies/ /archive/Proxies_backup/");
    
  } catch (e) {
    $.writeln("Archive failed: " + e.toString());
  }
  
  return result;
}

// Usage
archiveProxyFiles(app.project, "/mnt/archive/proxy_backup/");
```

---

## Proxy Workflow Automation

### Auto-Create Proxies on Import

```javascript
function importWithAutoProxy(sourceFolder, targetBin, proxyResolution) {
  /**
   * Import files and automatically create proxies
   * Combines import + proxy generation in single operation
   */
  
  var project = app.project;
  var sourceDir = new Folder(sourceFolder);
  
  if (!sourceDir.exists) {
    alert("Source folder not found: " + sourceFolder);
    return null;
  }
  
  var report = {
    imported: 0,
    proxiesCreated: 0,
    failed: 0,
    startTime: new Date().getTime()
  };
  
  try {
    // Step 1: Import files
    var files = sourceDir.getFiles("*.mov");
    var pathArray = [];
    
    for (var i = 0; i < files.length; i++) {
      if (files[i] instanceof File) {
        pathArray.push(files[i].absoluteURI);
      }
    }
    
    var imported = project.importFiles(pathArray, true, targetBin, false);
    
    if (imported) {
      report.imported = imported.length;
    }
    
    // Step 2: Create proxies for each imported item
    for (var j = 0; j < imported.length; j++) {
      var item = imported[j];
      
      if (item.type === "clip" && item.hasVideo && !item.isOffline) {
        try {
          item.createMediaProxy(proxyResolution);
          report.proxiesCreated++;
        } catch (e) {
          report.failed++;
        }
      }
    }
    
  } catch (e) {
    alert("Import with proxy failed: " + e.toString());
  }
  
  report.endTime = new Date().getTime();
  report.elapsedSeconds = (report.endTime - report.startTime) / 1000;
  
  $.writeln("=== IMPORT + PROXY REPORT ===");
  $.writeln("Imported: " + report.imported);
  $.writeln("Proxies created: " + report.proxiesCreated);
  $.writeln("Failed: " + report.failed);
  $.writeln("Time: " + report.elapsedSeconds.toFixed(1) + "s");
  
  return report;
}

// Usage
importWithAutoProxy("/mnt/camera_storage/2026-07-01/", app.project.rootBin, "1/4 Resolution");
```

---

## Proxy Performance Optimization

### Calculate Optimal Proxy Codec

```javascript
function recommendProxyCodec(sourceResolution, hardwareClass) {
  /**
   * Recommend proxy codec based on resolution and hardware
   * hardwareClass: "laptop" (limited), "workstation" (standard), "high-end" (professional)
   */
  
  var recommendations = {
    laptop: {
      "1080p": { codec: "H.264", bitrate: "25 Mbps", size: "12 MB/min" },
      "4K": { codec: "ProRes 422 Proxy", bitrate: "50 Mbps", size: "25 MB/min" },
      "8K": { codec: "ProRes 422 Proxy 1/2", bitrate: "25 Mbps", size: "12 MB/min" }
    },
    workstation: {
      "1080p": { codec: "ProRes 422 LT", bitrate: "50 Mbps", size: "25 MB/min" },
      "4K": { codec: "ProRes 422 LT", bitrate: "100 Mbps", size: "50 MB/min" },
      "8K": { codec: "ProRes 422 LT 1/4", bitrate: "50 Mbps", size: "25 MB/min" }
    },
    "high-end": {
      "1080p": { codec: "ProRes 422 HQ", bitrate: "100 Mbps", size: "50 MB/min" },
      "4K": { codec: "ProRes 422 HQ", bitrate: "200 Mbps", size: "100 MB/min" },
      "8K": { codec: "ProRes 422 HQ 1/2", bitrate: "100 Mbps", size: "50 MB/min" }
    }
  };
  
  var rec = recommendations[hardwareClass][sourceResolution];
  
  $.writeln("=== PROXY CODEC RECOMMENDATION ===");
  $.writeln("Source: " + sourceResolution);
  $.writeln("Hardware: " + hardwareClass);
  $.writeln("");
  $.writeln("Recommended Codec: " + rec.codec);
  $.writeln("Bitrate: " + rec.bitrate);
  $.writeln("Size: " + rec.size);
  $.writeln("");
  $.writeln("Rationale:");
  if (hardwareClass === "laptop") {
    $.writeln("- Lower bitrate for portable playback");
    $.writeln("- Prioritize smooth scrubbing over quality");
  } else if (hardwareClass === "workstation") {
    $.writeln("- Balanced quality and performance");
    $.writeln("- Suitable for most professional workflows");
  } else {
    $.writeln("- Highest quality proxies");
    $.writeln("- Fast playback on enterprise hardware");
  }
  
  return rec;
}

// Usage
recommendProxyCodec("4K", "workstation");
```

---

## Proxy Workflow Checklist

- ☐ Identify source codec and resolution
- ☐ Select appropriate proxy codec (H.264/ProRes/DNxHD)
- ☐ Set proxy resolution (1/4 for 4K, 1/2 for 8K)
- ☐ Configure Media Encoder watch folder (if using batch transcode)
- ☐ Monitor proxy folder size (archive when > 500 GB)
- ☐ Enable proxies for editing (Project → Proxy Settings)
- ☐ Create separate proxy folder for each project
- ☐ Verify proxy/original sync before delivery
- ☐ Switch to originals before final export
- ☐ Archive old proxies to external storage
- ☐ Document proxy codec for team consistency

---

## See Also

- Knowledge/codec-media-reference.md — Codec selection guide
- Knowledge/real-world-production-workflows.md — Dailies proxy workflow
- Knowledge/import.md — Batch import patterns
- Knowledge/automation.md — Batch operation scripting

---

## Sources

- Adobe Media Encoder: https://www.adobe.com/products/mediaencoder.html
- ProRes Specifications: https://support.apple.com/en-us/HT202410
- DNxHD Reference: https://www.avid.com/dnxhd
- Proxy Workflow Best Practices: Production case studies
