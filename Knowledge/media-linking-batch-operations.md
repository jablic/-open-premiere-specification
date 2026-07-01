---
id: media-linking-batch-operations
title: Media Linking, Relinking & Batch Ingestion
category: workflow
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC"
deprecated: null
eol: null
min_premiere_version: null
api_namespace: app
languages: [extendscript, javascript, typescript, python]
tags: [import, media-linking, relink, offline-media, batch-import, codec-detection, proxy-workflow]
related: [import, export-rendering-media-encoder, automation, best-practices]
supersedes: []
superseded_by: []
sources:
  - https://helpx.adobe.com/premiere/desktop/organize-media/file-organization/relink-offline-media-automatically.html
  - https://helpx.adobe.com/premiere-pro/using/relinking-media.html
  - https://ppro-scripting.docsforadobe.dev/print_page/
  - https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
  - https://github.com/AdobeDocs/uxp-premiere-pro-samples
confidence: medium
last_verified: "2026-07-01"
verified_against_version: "25.x / 26.0"
---

# Media Linking, Relinking & Batch Ingestion

> Handle offline clips, relink broken media, batch-import with codec detection, and manage media
> proxies programmatically — critical for production pipelines that move files or manage large codecs.

## TL;DR
- **Offline media:** Clips become "offline" when source files are moved/renamed/deleted. Premiere marks them with offline icon; manual relink via UI or programmatic relink via API.
- **Relink strategies:** (1) Automatic by filename/extension match; (2) Manual mapping via ProjectItem swap; (3) Proxy workflow (high-quality media linked to proxies).
- **Batch import:** ExtendScript `app.project.importFiles()` or UXP `project.importFiles()` (async); detect codec/resolution post-import via ProjectItem metadata.
- **Codec detection:** ProjectItem has no direct "codec" property; infer from filename extension or use QE DOM for detailed inspection.

## Status & Lifecycle
- **ExtendScript:** Stable, synchronous; supported through Sept 2026.
- **UXP:** Current (25.6+), async; `importFiles()` improved in 26.0 beta.
- **UI relink dialog:** Manual fallback; Adobe's automatic relink heuristic works well for standard workflows.

## Architecture

### Media linking scope
```
Project
  ├─ sequences[i]
  │   └─ tracks[j]
  │       └─ trackItems[k]  ← clips referencing media
  └─ projectItems[m]        ← media bins/folders holding source references
```

A **clip** (TrackItem) has a `projectItem` reference pointing to its media source. When the source file is deleted/moved, the `projectItem` becomes offline, and the clip's media cannot play.

### Offline detection

```javascript
// ExtendScript
var projectItem = /* get from clip */;
var isOffline = projectItem.isOffline;  // boolean

if (isOffline) {
  // Try to relink programmatically
  projectItem.linkMedia("/path/to/replacement.mov");
}
```

## API Surface

### ExtendScript — import & relink

```javascript
// ExtendScript — batch import media
var importedItems = app.project.importFiles(
  ["/path/to/video1.mov", "/path/to/video2.mov"],
  true,  // suppressUI: true = don't show dialog
  app.project.rootBin,  // target bin
  false  // importAsNumberedStills: false for normal clips
);

if (importedItems && importedItems.length > 0) {
  for (var i = 0; i < importedItems.length; i++) {
    var item = importedItems[i];
    // item is now a ProjectItem; can be used in sequences
  }
}
```

```javascript
// ExtendScript — relink offline clip
var projectItem = /* ... */;
if (projectItem.isOffline) {
  try {
    projectItem.linkMedia("/Volumes/archive/footage_v2.mov");
    alert("Relinked: " + projectItem.name);
  } catch (e) {
    alert("Relink failed: " + e.toString());
  }
}
```

### UXP — async import

```javascript
// UXP — Premiere 25.6+
const { application } = require("premierepro");

(async () => {
  const project = await application.activeProject;
  
  // Import files (returns boolean success, not the items)
  const success = await project.importFiles(
    ["/path/to/video1.mov", "/path/to/video2.mov"],
    false,  // suppressUI
    null    // targetBin (null = root)
  );

  if (success) {
    console.log("Import succeeded");
    // Note: UXP does NOT return the imported items; you must query the project after import
    const allItems = await project.projectItems;
    // Find newly imported items by name/timestamp (workaround — not ideal)
  } else {
    console.error("Import failed");
  }
})();
```

**Gotcha:** UXP's `importFiles()` returns a boolean, not the list of imported ProjectItems. Determining which items were just imported requires post-import querying or external tracking.

### ProjectItem properties (offline detection)

| Property | Type | Notes |
|---|---|---|
| `name` | String | Display name |
| `isOffline` | Boolean | True if source file missing |
| `filePath` | String | (ExtendScript only; unavailable in UXP) Full path to media |
| `hasProxy` | Boolean | True if proxy is linked |
| `proxyPath` | String | (ExtendScript only) Path to proxy file |

## Working Examples

### Example 1: Batch relink by filename match (ExtendScript)

```javascript
// ExtendScript — safe offline relink with fallback
function batchRelinkOfflineMedia(sequence, mediaSearchRoots) {
  // mediaSearchRoots: array of folder paths to search for replacements
  
  var track, item, projectItem;
  var relinked = 0, failed = 0;

  for (var t = 0; t < sequence.videoTracks.length; t++) {
    track = sequence.videoTracks[t];
    
    for (var i = 0; i < track.clips.length; i++) {
      item = track.clips[i];
      projectItem = item.projectItem;
      
      if (projectItem && projectItem.isOffline) {
        var originalName = projectItem.name;
        var found = false;
        
        // Search for replacement by name
        for (var r = 0; r < mediaSearchRoots.length; r++) {
          var folder = new Folder(mediaSearchRoots[r]);
          var files = folder.getFiles(originalName + ".*");  // fuzzy match
          
          if (files && files.length > 0) {
            try {
              projectItem.linkMedia(files[0].fullName);
              $.writeln("✓ Relinked: " + originalName);
              relinked++;
              found = true;
              break;
            } catch (e) {
              $.writeln("✗ Relink error: " + e.toString());
              failed++;
            }
          }
        }
        
        if (!found) {
          $.writeln("⚠ Not found: " + originalName);
          failed++;
        }
      }
    }
  }
  
  alert("Relinked: " + relinked + " | Failed/Missing: " + failed);
}

// Usage
var seq = app.project.activeSequence;
var searchPaths = ["/Volumes/archive/footage", "/Volumes/backup/media"];
batchRelinkOfflineMedia(seq, searchPaths);
```

### Example 2: Codec/resolution detection (ExtendScript + QE DOM workaround)

```javascript
// ExtendScript — detect codec/resolution via QE DOM
function detectMediaProperties(projectItem) {
  // Note: Direct ProjectItem codec API missing; use QE DOM as workaround
  
  if (!projectItem || !projectItem.media) {
    return { codec: "unknown", resolution: "unknown", fps: "unknown" };
  }

  try {
    // Enable QE to access detailed metadata
    app.enableQE();
    
    var mediaObj = projectItem.media;
    
    // Infer codec from file extension
    var ext = projectItem.filePath ? projectItem.filePath.split(".").pop().toLowerCase() : "unknown";
    var codecMap = {
      "mov": "ProRes/DNxHD (likely)",
      "mp4": "H.264",
      "mxf": "Avid DNxHD/ProRes",
      "dng": "DNG sequence",
      "r3d": "RED RAW"
    };
    var codec = codecMap[ext] || ext.toUpperCase();
    
    // Try to get resolution from QE
    var videoInfo = app.project.getWindowObject("Premiere Pro", "Project");  // QE query (fragile)
    
    return {
      codec: codec,
      extension: ext,
      name: projectItem.name,
      isOffline: projectItem.isOffline
    };
  } catch (e) {
    return { error: e.toString() };
  }
}

// Usage
var projectItem = app.project.rootBin.children[0];  // first item in root bin
var props = detectMediaProperties(projectItem);
alert("Codec: " + props.codec + " | Ext: " + props.extension);
```

### Example 3: Batch import with verification (ExtendScript)

```javascript
// ExtendScript — safe batch import with per-file logging
function batchImportWithLog(filePaths, logPath) {
  var log = [];
  var imported = [];
  
  for (var i = 0; i < filePaths.length; i++) {
    var filePath = filePaths[i];
    var file = new File(filePath);
    
    if (!file.exists) {
      log.push("SKIP: File not found: " + filePath);
      continue;
    }
    
    try {
      var items = app.project.importFiles([filePath], true, app.project.rootBin, false);
      if (items && items.length > 0) {
        imported.push(items[0]);
        log.push("OK: Imported " + items[0].name);
      } else {
        log.push("WARN: Import returned no items for: " + filePath);
      }
    } catch (e) {
      log.push("ERROR: " + filePath + " - " + e.toString());
    }
  }
  
  // Write log to file
  var logFile = new File(logPath);
  logFile.open("w");
  logFile.write(log.join("\n"));
  logFile.close();
  
  return {
    total: filePaths.length,
    imported: imported.length,
    failed: filePaths.length - imported.length,
    items: imported,
    logPath: logPath
  };
}

// Usage
var files = [
  "/Volumes/media/clip_001.mov",
  "/Volumes/media/clip_002.mov",
  "/Volumes/media/missing.mov"
];
var result = batchImportWithLog(files, "/tmp/import_log.txt");
alert("Imported: " + result.imported + " / " + result.total);
```

### Example 4: Proxy workflow setup (ExtendScript)

```javascript
// ExtendScript — link proxy media to high-quality original
function linkProxyToMedia(projectItem, proxyPath) {
  // Set up a proxy for offline editing
  
  if (!projectItem) {
    alert("No project item");
    return false;
  }

  try {
    // Create proxy link (ExtendScript API is limited; use UI dialog as fallback)
    // Direct proxy API may not be available; use workaround:
    // 1. Import proxy file as separate item
    var proxyItems = app.project.importFiles([proxyPath], true, app.project.rootBin, false);
    
    if (proxyItems && proxyItems.length > 0) {
      // Note: Full programmatic proxy linking is mostly UI-driven in Premiere
      alert("Proxy imported; use Premiere UI (Clip > Link Proxy) to link:\n" + 
            "Original: " + projectItem.name + "\nProxy: " + proxyItems[0].name);
      return true;
    }
  } catch (e) {
    alert("Error: " + e.toString());
    return false;
  }
}

// Usage
var item = app.project.rootBin.children[0];
linkProxyToMedia(item, "/Volumes/proxies/clip_proxy.mov");
```

## Limitations

- **No codec property on ProjectItem.** Must infer from filename or use fragile QE DOM queries.
- **UXP importFiles() returns boolean, not item list.** Post-import item discovery is manual and unreliable.
- **No programmatic proxy linking in ExtendScript/UXP.** Proxy setup mostly manual via UI.
- **Offline relink doesn't verify media compatibility.** If you relink to a different codec/resolution, clips may play incorrectly or show artifacts.
- **No batch relink completion callback.** Relink operations are fire-and-forget; UI does not notify script when complete.

## Common Errors & Gotchas

- **Symptom:** `importFiles()` succeeds but items don't appear in UI. **Cause:** Bin not refreshed; UI lag. **Fix:** Wait briefly or manually refresh bin view.
- **Symptom:** Relink fails silently; no error thrown. **Cause:** File permissions or codec mismatch. **Fix:** Check file exists, readable, and codec matches original.
- **Symptom:** (UXP) Don't know which items were just imported. **Cause:** API returns boolean, not items. **Fix:** Query project item list post-import and compare timestamps.
- **Symptom:** Batch relink takes forever. **Cause:** Searching network paths. **Fix:** Limit search scope or provide explicit paths.

## Workarounds

- **For codec detection:** Maintain external metadata file (JSON) mapping filenames to codecs; query at import time.
- **For proxy linking:** Store (original_name, proxy_path) mapping externally; UI relink dialog will match by name if proxy file is in expected location.
- **For batch relinking:** Use file naming convention (e.g., `clip_name.mov` → `clip_name_proxy.mov`) to automate path construction.

## Migration (ExtendScript → UXP)

| ExtendScript | UXP (25.6+) |
|---|---|
| `app.project.importFiles(paths)` → returns items | `project.importFiles(paths)` → returns boolean; items must be queried |
| `projectItem.filePath` | `projectItem.filePath` (may not be available in UXP) |
| `projectItem.linkMedia(path)` | TBD (not documented in UXP 25.6; use ExtendScript bridge) |
| Sync | Async; must await |

## Cross-References
- `import` — general media import API reference
- `export-rendering-media-encoder` — exporting with linked media intact
- `sequences-tracks-trackitems` — TrackItem/ProjectItem relationship
- `automation` — batch workflow patterns

## Sources
- https://helpx.adobe.com/premiere/desktop/organize-media/file-organization/relink-offline-media-automatically.html
- https://helpx.adobe.com/premiere-pro/using/relinking-media.html
- https://ppro-scripting.docsforadobe.dev/print_page/
- https://developer.adobe.com/premiere-pro/uxp/ppro-reference/
- https://github.com/AdobeDocs/uxp-premiere-pro-samples
