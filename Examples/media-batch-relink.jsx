/**
 * Batch Media Relinking & Import
 *
 * Runtime: ExtendScript (ES3) for Premiere Pro 14.x–25.x
 *
 * Purpose:
 * - Batch import media files with logging
 * - Find and relink offline media by filename match
 * - Detect codec/resolution from filename
 * - Export project with all media status
 *
 * Topic doc: media-linking-batch-operations.md
 */

// ============================================================================
// MAIN: Batch relink and import workflow
// ============================================================================

function main() {
  var project = app.project;
  if (!project) {
    alert("ERROR: No project open.");
    return;
  }

  // Example workflow:
  // 1. Relink offline media in active sequence
  // 2. Import new media files
  // 3. Generate report

  var seq = project.activeSequence;
  if (!seq) {
    alert("ERROR: No active sequence. Please open a sequence first.");
    return;
  }

  // Define search paths for relinking
  var searchPaths = [
    "/Volumes/archive/footage",
    "/Volumes/backup/media",
    Folder.desktop.toString()  // User can change this
  ];

  var report = {
    relinked: [],
    stillOffline: [],
    imported: [],
    errors: []
  };

  // Step 1: Relink offline media
  alert("Step 1/2: Finding offline media...\n\nSearching in:\n" + searchPaths.join("\n"));
  relinkOfflineMedia(seq, searchPaths, report);

  // Step 2: Option to import additional files
  var importMore = confirm("Step 2/2: Import additional media files?\n\n(Click OK to browse for files)");
  if (importMore) {
    var filesToImport = File.openDialog(
      "Select media files to import",
      "All files:*.*",
      true  // allow multiple selection
    );

    if (filesToImport && filesToImport.length > 0) {
      var filePaths = [];
      for (var i = 0; i < filesToImport.length; i++) {
        filePaths.push(filesToImport[i].toString());
      }
      batchImportMedia(project, filePaths, report);
    }
  }

  // Step 3: Report
  showReport(report);
  exportReport(report, "/tmp/media_relink_report.txt");
}

// ============================================================================
// RELINK OFFLINE MEDIA
// ============================================================================

function relinkOfflineMedia(sequence, searchPaths, report) {
  /**
   * Find offline clips in sequence, search for replacements, relink
   */

  if (!sequence || !sequence.videoTracks) {
    report.errors.push("Invalid sequence");
    return;
  }

  for (var t = 0; t < sequence.videoTracks.length; t++) {
    var track = sequence.videoTracks[t];

    for (var i = 0; i < track.clips.length; i++) {
      var clip = track.clips[i];
      var projectItem = clip.projectItem;

      if (projectItem && projectItem.isOffline) {
        var originalName = projectItem.name;
        var found = false;

        // Search for replacement
        for (var r = 0; r < searchPaths.length; r++) {
          var folder = new Folder(searchPaths[r]);
          if (!folder.exists) continue;

          // Try exact filename match with wildcards for extension
          var files = folder.getFiles(originalName.replace(/\.\w+$/, "") + ".*");

          if (files && files.length > 0) {
            try {
              projectItem.linkMedia(files[0].toString());
              report.relinked.push({
                name: originalName,
                linkedTo: files[0].toString(),
                codec: detectCodec(files[0].toString())
              });
              found = true;
              break;
            } catch (e) {
              report.errors.push("Relink error for " + originalName + ": " + e.toString());
            }
          }
        }

        if (!found) {
          report.stillOffline.push(originalName);
        }
      }
    }
  }
}

// ============================================================================
// BATCH IMPORT MEDIA
// ============================================================================

function batchImportMedia(project, filePaths, report) {
  /**
   * Import multiple media files with per-file logging
   */

  if (!project || !project.rootBin) {
    report.errors.push("Invalid project");
    return;
  }

  for (var i = 0; i < filePaths.length; i++) {
    var filePath = filePaths[i];
    var file = new File(filePath);

    if (!file.exists) {
      report.errors.push("File not found: " + filePath);
      continue;
    }

    try {
      var items = project.importFiles(
        [filePath],
        true,  // suppressUI
        project.rootBin,
        false  // importAsNumberedStills
      );

      if (items && items.length > 0) {
        var item = items[0];
        report.imported.push({
          name: item.name,
          path: filePath,
          codec: detectCodec(filePath),
          imported_at: new Date().toString()
        });
      } else {
        report.errors.push("Import returned no items for: " + filePath);
      }

    } catch (e) {
      report.errors.push("Import error: " + filePath + " - " + e.toString());
    }
  }
}

// ============================================================================
// CODEC DETECTION (filename-based heuristic)
// ============================================================================

function detectCodec(filePath) {
  /**
   * Infer codec from file extension (heuristic only)
   */

  var ext = filePath.split(".").pop().toLowerCase();
  var codecMap = {
    "mov": "ProRes/DNxHD (likely)",
    "mp4": "H.264",
    "mxf": "Avid DNxHD/ProRes",
    "dng": "DNG sequence",
    "r3d": "RED RAW",
    "avi": "DV/Uncompressed",
    "m2t": "MPEG2-TS",
    "mts": "AVCHD"
  };

  return codecMap[ext] ? codecMap[ext] + " (." + ext + ")" : ext.toUpperCase() + " (unknown)";
}

// ============================================================================
// REPORTING
// ============================================================================

function showReport(report) {
  /**
   * Display report in alert dialog
   */

  var msg = "=== MEDIA RELINKING REPORT ===\n\n";

  if (report.relinked.length > 0) {
    msg += "✓ RELINKED (" + report.relinked.length + "):\n";
    for (var i = 0; i < Math.min(report.relinked.length, 5); i++) {
      var r = report.relinked[i];
      msg += "  • " + r.name + " → " + r.codec + "\n";
    }
    if (report.relinked.length > 5) {
      msg += "  ... and " + (report.relinked.length - 5) + " more\n";
    }
    msg += "\n";
  }

  if (report.stillOffline.length > 0) {
    msg += "✗ STILL OFFLINE (" + report.stillOffline.length + "):\n";
    for (var i = 0; i < Math.min(report.stillOffline.length, 5); i++) {
      msg += "  • " + report.stillOffline[i] + "\n";
    }
    if (report.stillOffline.length > 5) {
      msg += "  ... and " + (report.stillOffline.length - 5) + " more\n";
    }
    msg += "\n";
  }

  if (report.imported.length > 0) {
    msg += "⬇️  IMPORTED (" + report.imported.length + "):\n";
    for (var i = 0; i < Math.min(report.imported.length, 5); i++) {
      var imp = report.imported[i];
      msg += "  • " + imp.name + " (" + imp.codec + ")\n";
    }
    if (report.imported.length > 5) {
      msg += "  ... and " + (report.imported.length - 5) + " more\n";
    }
    msg += "\n";
  }

  if (report.errors.length > 0) {
    msg += "⚠️  ERRORS (" + report.errors.length + "):\n";
    for (var i = 0; i < Math.min(report.errors.length, 3); i++) {
      msg += "  • " + report.errors[i] + "\n";
    }
    if (report.errors.length > 3) {
      msg += "  ... and " + (report.errors.length - 3) + " more\n";
    }
  }

  msg += "\n=== END REPORT ===";

  alert(msg);
}

function exportReport(report, outputPath) {
  /**
   * Save detailed report to text file
   */

  var txt = "MEDIA RELINKING REPORT\n";
  txt += "Generated: " + new Date().toString() + "\n";
  txt += "=====================================\n\n";

  txt += "RELINKED (" + report.relinked.length + "):\n";
  for (var i = 0; i < report.relinked.length; i++) {
    var r = report.relinked[i];
    txt += "  [" + i + "] " + r.name + "\n";
    txt += "       → " + r.linkedTo + "\n";
    txt += "       Codec: " + r.codec + "\n";
  }

  txt += "\nSTILL OFFLINE (" + report.stillOffline.length + "):\n";
  for (var i = 0; i < report.stillOffline.length; i++) {
    txt += "  [" + i + "] " + report.stillOffline[i] + "\n";
  }

  txt += "\nIMPORTED (" + report.imported.length + "):\n";
  for (var i = 0; i < report.imported.length; i++) {
    var imp = report.imported[i];
    txt += "  [" + i + "] " + imp.name + "\n";
    txt += "       Path: " + imp.path + "\n";
    txt += "       Codec: " + imp.codec + "\n";
  }

  txt += "\nERRORS (" + report.errors.length + "):\n";
  for (var i = 0; i < report.errors.length; i++) {
    txt += "  [" + i + "] " + report.errors[i] + "\n";
  }

  txt += "\n=====================================\n";
  txt += "End of report\n";

  // Write file
  try {
    var file = new File(outputPath);
    file.open("w");
    file.write(txt);
    file.close();
    $.writeln("Report saved to: " + outputPath);
  } catch (e) {
    alert("Failed to save report: " + e.toString());
  }
}

// ============================================================================
// EXECUTE
// ============================================================================

main();
