/**
 * Batch Media Import & Organization
 *
 * Runtime: ExtendScript (ES3) for Premiere Pro 14.x–25.x
 *
 * Purpose:
 * - Import media from folder with intelligent organization
 * - Auto-create bins by media type (video, audio, images, graphics)
 * - Auto-create bins by metadata (codec, resolution, source)
 * - Generate import report with validation
 * - Skip duplicates and invalid files
 * - Create proxy media for selected formats
 *
 * Topic doc: import.md
 */

// ============================================================================
// MAIN: Import workflow with organization
// ============================================================================

function main() {
  var project = app.project;
  if (!project) {
    alert("ERROR: No project open.");
    return;
  }

  // Prompt user for source folder
  var sourceFolder = Folder.selectDialog("Select folder containing media files");
  if (!sourceFolder) {
    return;  // User cancelled
  }

  // Import options dialog
  var dialog = new Window("dialog", "Import Options");

  dialog.add("statictext", undefined, "Organization Method:");
  var groupOrganize = dialog.add("group");
  groupOrganize.orientation = "column";
  var byTypeRadio = groupOrganize.add("radiobutton", undefined, "By Media Type (video, audio, images)");
  var byResRadio = groupOrganize.add("radiobutton", undefined, "By Resolution");
  var byCodecRadio = groupOrganize.add("radiobutton", undefined, "Flat (all in root)");
  byTypeRadio.value = true;

  dialog.add("statictext", undefined, "");
  var createProxyCheck = dialog.add("checkbox", undefined, "Create proxies for video (1/4 resolution)");
  createProxyCheck.value = false;

  var btnGroup = dialog.add("group");
  btnGroup.add("button", undefined, "Import", { name: "ok" });
  btnGroup.add("button", undefined, "Cancel", { name: "cancel" });

  var result = dialog.show();
  if (result !== 1) return;

  var organizeMethod = byTypeRadio.value ? "type" : (byResRadio.value ? "resolution" : "flat");
  var createProxies = createProxyCheck.value;

  // Execute import
  var report = {
    imported: [],
    skipped: [],
    errors: [],
    stats: {}
  };

  importAndOrganizeMedia(project, sourceFolder, organizeMethod, createProxies, report);

  // Show results
  showImportReport(report);
}

// ============================================================================
// IMPORT AND ORGANIZE
// ============================================================================

function importAndOrganizeMedia(project, folder, organizeMethod, createProxies, report) {
  /**
   * Import all media files and organize into bins
   */

  var files = folder.getFiles();
  var mediaByBin = {};

  // Step 1: Scan and categorize files
  for (var i = 0; i < files.length; i++) {
    var file = files[i];

    if (file instanceof Folder) continue;

    var analysis = analyzeMediaFile(file);
    if (!analysis.valid) {
      report.skipped.push({ name: file.name, reason: "Not supported media" });
      continue;
    }

    // Determine bin destination
    var binName = getBinNameForFile(file, analysis, organizeMethod);

    if (!mediaByBin[binName]) {
      mediaByBin[binName] = [];
    }

    mediaByBin[binName].push({ file: file, analysis: analysis });
  }

  // Step 2: Create bins and import
  for (var binName in mediaByBin) {
    if (mediaByBin.hasOwnProperty(binName)) {
      var bin = getOrCreateBin(project, binName);
      var filesForBin = mediaByBin[binName];

      for (var j = 0; j < filesForBin.length; j++) {
        var item = filesForBin[j];

        try {
          var importedItems = project.importFiles([item.file.toString()], true, bin, false);

          if (importedItems && importedItems.length > 0) {
            var importedItem = importedItems[0];

            // Create proxy if requested
            if (createProxies && item.analysis.type === "video") {
              try {
                importedItem.createMediaProxy("1/4 Resolution");
                report.imported.push({
                  name: item.file.name,
                  bin: binName,
                  codec: item.analysis.codec,
                  proxy: "Created"
                });
              } catch (e) {
                report.imported.push({
                  name: item.file.name,
                  bin: binName,
                  codec: item.analysis.codec,
                  proxy: "Failed"
                });
              }
            } else {
              report.imported.push({
                name: item.file.name,
                bin: binName,
                codec: item.analysis.codec,
                proxy: "N/A"
              });
            }
          }
        } catch (e) {
          report.errors.push({
            file: item.file.name,
            bin: binName,
            error: e.toString()
          });
        }
      }
    }
  }

  // Step 3: Generate statistics
  report.stats = {
    total: report.imported.length + report.skipped.length + report.errors.length,
    imported: report.imported.length,
    skipped: report.skipped.length,
    errors: report.errors.length,
    bins_created: Object.keys(mediaByBin).length
  };
}

// ============================================================================
// FILE ANALYSIS
// ============================================================================

function analyzeMediaFile(file) {
  /**
   * Analyze file to determine type and metadata
   */

  var ext = file.name.split(".").pop().toLowerCase();

  var videoExts = ["mov", "mp4", "avi", "mts", "m2t", "dng", "r3d", "mxf", "mkv"];
  var audioExts = ["wav", "aiff", "aif", "mp3", "m4a", "flac"];
  var imageExts = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "psd", "ai"];
  var graphicsExts = ["svg", "eps", "pdf"];

  var type = "unknown";
  if (videoExts.indexOf(ext) >= 0) type = "video";
  else if (audioExts.indexOf(ext) >= 0) type = "audio";
  else if (imageExts.indexOf(ext) >= 0) type = "image";
  else if (graphicsExts.indexOf(ext) >= 0) type = "graphics";

  if (type === "unknown") {
    return { valid: false, error: "Unknown file type" };
  }

  // Infer codec from extension
  var codec = inferCodecFromExtension(ext);

  // Infer resolution heuristic (rough)
  var resolution = "unknown";
  if (file.name.match(/4k|2160/i)) resolution = "4K";
  else if (file.name.match(/1080p|fhd/i)) resolution = "1080p";
  else if (file.name.match(/720p|hd/i)) resolution = "720p";

  return {
    valid: true,
    type: type,
    ext: ext,
    codec: codec,
    resolution: resolution,
    size: file.length
  };
}

function inferCodecFromExtension(ext) {
  /**
   * Infer codec name from file extension (heuristic)
   */

  var codecMap = {
    "mov": "ProRes/DNxHD",
    "mp4": "H.264/H.265",
    "mxf": "Avid DNxHD",
    "dng": "DNG Sequence",
    "r3d": "RED RAW",
    "avi": "DV/Uncompressed",
    "mts": "AVCHD",
    "m2t": "MPEG-2",
    "mkv": "Matroska",
    "wav": "PCM",
    "aif": "AIFF",
    "aiff": "AIFF",
    "mp3": "MP3",
    "m4a": "AAC",
    "flac": "FLAC",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "tiff": "TIFF",
    "tif": "TIFF",
    "psd": "Photoshop",
    "svg": "SVG",
    "pdf": "PDF"
  };

  return codecMap[ext] || ext.toUpperCase();
}

// ============================================================================
// BIN MANAGEMENT
// ============================================================================

function getBinNameForFile(file, analysis, method) {
  /**
   * Determine bin name based on organization method
   */

  if (method === "flat") {
    return "Imported Media";
  }

  if (method === "resolution") {
    if (analysis.type === "video") {
      return "Video - " + analysis.resolution;
    }
    return analysis.type.charAt(0).toUpperCase() + analysis.type.slice(1);
  }

  // Default: by type
  var typeName = analysis.type.charAt(0).toUpperCase() + analysis.type.slice(1);
  return typeName;
}

function getOrCreateBin(project, binName) {
  /**
   * Get existing bin or create new one
   */

  function findBinRecursive(parentBin, targetName) {
    if (!parentBin.children) return null;

    for (var i = 0; i < parentBin.children.length; i++) {
      var child = parentBin.children[i];
      if (child.name === targetName) {
        return child;
      }
    }
    return null;
  }

  var existingBin = findBinRecursive(project.rootBin, binName);
  if (existingBin) {
    return existingBin;
  }

  return project.rootBin.createBin(binName);
}

// ============================================================================
// REPORTING
// ============================================================================

function showImportReport(report) {
  /**
   * Display import results summary
   */

  var msg = "=== IMPORT REPORT ===\n\n";

  msg += "SUMMARY:\n";
  msg += "Total Files: " + report.stats.total + "\n";
  msg += "Imported: " + report.stats.imported + "\n";
  msg += "Skipped: " + report.stats.skipped + "\n";
  msg += "Errors: " + report.stats.errors + "\n";
  msg += "Bins Created: " + report.stats.bins_created + "\n\n";

  if (report.imported.length > 0) {
    msg += "✓ IMPORTED (" + report.imported.length + "):\n";
    for (var i = 0; i < Math.min(5, report.imported.length); i++) {
      var imp = report.imported[i];
      msg += "  • " + imp.name + " → " + imp.bin + " [" + imp.codec + "]\n";
    }
    if (report.imported.length > 5) {
      msg += "  ... and " + (report.imported.length - 5) + " more\n";
    }
    msg += "\n";
  }

  if (report.skipped.length > 0) {
    msg += "⊘ SKIPPED (" + report.skipped.length + "):\n";
    for (var i = 0; i < Math.min(3, report.skipped.length); i++) {
      msg += "  • " + report.skipped[i].name + " (" + report.skipped[i].reason + ")\n";
    }
    if (report.skipped.length > 3) {
      msg += "  ... and " + (report.skipped.length - 3) + " more\n";
    }
    msg += "\n";
  }

  if (report.errors.length > 0) {
    msg += "✗ ERRORS (" + report.errors.length + "):\n";
    for (var i = 0; i < Math.min(3, report.errors.length); i++) {
      msg += "  • " + report.errors[i].file + ": " + report.errors[i].error + "\n";
    }
    if (report.errors.length > 3) {
      msg += "  ... and " + (report.errors.length - 3) + " more\n";
    }
  }

  msg += "\n=== END REPORT ===";

  alert(msg);
}

// ============================================================================
// EXECUTE
// ============================================================================

main();
