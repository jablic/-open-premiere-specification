/**
 * Batch Caption Reader & SRT/CSV Exporter
 *
 * Runtime: ExtendScript (ES3) for Premiere Pro 20.x–25.x
 *
 * Purpose:
 * - Extract all captions from active sequence
 * - Analyze caption timing, duration, text length
 * - Export to SRT (SubRip format) for external processing
 * - Export to CSV for Excel/data analysis
 * - Generate caption statistics and validation report
 *
 * Topic doc: captions.md
 */

// ============================================================================
// MAIN: Caption extraction and export workflow
// ============================================================================

function main() {
  var project = app.project;
  if (!project) {
    alert("ERROR: No project open.");
    return;
  }

  var seq = project.activeSequence;
  if (!seq) {
    alert("ERROR: No active sequence. Please open a sequence first.");
    return;
  }

  // Check for captions
  if (!seq.captionTracks || seq.captionTracks.length === 0) {
    alert("ERROR: No caption track in active sequence.");
    return;
  }

  var captionTrack = seq.captionTracks[0];
  if (!captionTrack || !captionTrack.captions || captionTrack.captions.length === 0) {
    alert("No captions found in sequence.");
    return;
  }

  // Step 1: Read all captions
  var captions = readCaptions(captionTrack);

  if (captions.length === 0) {
    alert("ERROR: Failed to read captions.");
    return;
  }

  // Step 2: Generate statistics
  var stats = generateStatistics(captions);

  // Step 3: Show summary
  showSummary(captions, stats);

  // Step 4: Export options
  var exportChoice = confirm(
    "Export captions?\n\n" +
    "OK = Export to SRT + CSV\n" +
    "Cancel = Show stats only"
  );

  if (exportChoice) {
    exportCaptions(captions, seq.name);
  }
}

// ============================================================================
// READ CAPTIONS
// ============================================================================

function readCaptions(captionTrack) {
  /**
   * Extract all captions from track with timing and text analysis
   */

  var captions = [];

  for (var i = 0; i < captionTrack.captions.length; i++) {
    var caption = captionTrack.captions[i];

    try {
      var startTime = caption.startTime;
      var endTime = caption.endTime;
      var text = caption.text || "";

      var captionObj = {
        index: i + 1,
        startTime: startTime,
        endTime: endTime,
        duration: endTime - startTime,
        text: text,
        textLength: text.length,
        wordCount: text.split(/\s+/).length,
        timestamp: formatSRTTime(startTime),
        endTimestamp: formatSRTTime(endTime),
        duration_sec: (endTime - startTime) / 254016000
      };

      captions.push(captionObj);
    } catch (e) {
      $.writeln("ERROR reading caption " + i + ": " + e.toString());
    }
  }

  return captions;
}

// ============================================================================
// STATISTICS & ANALYSIS
// ============================================================================

function generateStatistics(captions) {
  /**
   * Analyze caption data for patterns and validation
   */

  var stats = {
    totalCaptions: captions.length,
    totalDuration: 0,
    totalWords: 0,
    totalChars: 0,
    avgDuration: 0,
    avgWords: 0,
    avgChars: 0,
    longestCaption: { text: "", chars: 0, duration: 0 },
    shortestCaption: { text: "", chars: 9999, duration: 999999999 },
    overlappingCaptions: [],
    zeroLengthCaptions: [],
    issues: []
  };

  for (var i = 0; i < captions.length; i++) {
    var cap = captions[i];

    stats.totalDuration += cap.duration;
    stats.totalWords += cap.wordCount;
    stats.totalChars += cap.textLength;

    // Track longest/shortest
    if (cap.textLength > stats.longestCaption.chars) {
      stats.longestCaption = { text: cap.text, chars: cap.textLength, duration: cap.duration_sec };
    }
    if (cap.textLength < stats.shortestCaption.chars && cap.textLength > 0) {
      stats.shortestCaption = { text: cap.text, chars: cap.textLength, duration: cap.duration_sec };
    }

    // Detect issues
    if (cap.duration === 0) {
      stats.zeroLengthCaptions.push(i);
      stats.issues.push("Caption " + cap.index + ": zero duration");
    }

    if (cap.duration_sec > 15) {
      stats.issues.push("Caption " + cap.index + ": very long duration (" + cap.duration_sec.toFixed(2) + "s)");
    }

    // Check for overlaps
    if (i > 0 && captions[i - 1].endTime > cap.startTime) {
      stats.overlappingCaptions.push(i);
      stats.issues.push("Caption " + cap.index + " overlaps with " + captions[i - 1].index);
    }
  }

  // Calculate averages
  stats.avgDuration = stats.totalCaptions > 0 ? stats.totalDuration / stats.totalCaptions / 254016000 : 0;
  stats.avgWords = stats.totalCaptions > 0 ? stats.totalWords / stats.totalCaptions : 0;
  stats.avgChars = stats.totalCaptions > 0 ? stats.totalChars / stats.totalCaptions : 0;

  return stats;
}

// ============================================================================
// FORMATTING & TIME CONVERSION
// ============================================================================

function formatSRTTime(ticks) {
  /**
   * Convert Premiere ticks to SRT timecode format (HH:MM:SS,mmm)
   */

  var seconds = ticks / 254016000;
  var hours = Math.floor(seconds / 3600);
  var mins = Math.floor((seconds % 3600) / 60);
  var secs = Math.floor(seconds % 60);
  var ms = Math.floor((seconds % 1) * 1000);

  return pad(hours) + ":" + pad(mins) + ":" + pad(secs) + "," + padMs(ms);
}

function pad(n) {
  return (n < 10 ? "0" : "") + n;
}

function padMs(n) {
  return (n < 100 ? (n < 10 ? "00" : "0") : "") + n;
}

function formatSeconds(seconds) {
  /**
   * Format seconds as readable duration string
   */

  var h = Math.floor(seconds / 3600);
  var m = Math.floor((seconds % 3600) / 60);
  var s = Math.floor(seconds % 60);

  if (h > 0) return h + "h " + m + "m " + s + "s";
  if (m > 0) return m + "m " + s + "s";
  return s + "s";
}

// ============================================================================
// REPORTING
// ============================================================================

function showSummary(captions, stats) {
  /**
   * Display caption analysis in alert dialog
   */

  var msg = "=== CAPTION ANALYSIS REPORT ===\n\n";

  msg += "Total Captions: " + stats.totalCaptions + "\n";
  msg += "Total Duration: " + formatSeconds(stats.totalDuration / 254016000) + "\n";
  msg += "Avg Duration: " + stats.avgDuration.toFixed(2) + "s\n";
  msg += "Total Words: " + stats.totalWords + "\n";
  msg += "Avg Words/Caption: " + stats.avgWords.toFixed(1) + "\n";
  msg += "Total Characters: " + stats.totalChars + "\n";
  msg += "Avg Chars/Caption: " + stats.avgChars.toFixed(0) + "\n\n";

  msg += "Longest Caption: \"" + truncate(stats.longestCaption.text, 30) + "\" (" + stats.longestCaption.chars + " chars)\n";
  msg += "Shortest Caption: \"" + truncate(stats.shortestCaption.text, 30) + "\" (" + stats.shortestCaption.chars + " chars)\n\n";

  if (stats.issues.length > 0) {
    msg += "⚠️  ISSUES FOUND (" + stats.issues.length + "):\n";
    for (var i = 0; i < Math.min(5, stats.issues.length); i++) {
      msg += "  • " + stats.issues[i] + "\n";
    }
    if (stats.issues.length > 5) {
      msg += "  ... and " + (stats.issues.length - 5) + " more\n";
    }
  } else {
    msg += "✓ No issues detected\n";
  }

  msg += "\n=== END REPORT ===";

  alert(msg);
}

function truncate(str, len) {
  /**
   * Truncate string with ellipsis
   */

  return str.length > len ? str.substring(0, len) + "..." : str;
}

// ============================================================================
// EXPORT TO SRT
// ============================================================================

function exportToSRT(captions, outputPath) {
  /**
   * Export captions in SubRip (.srt) format
   * Format: index\ntimecode\ntext\n\n
   */

  var srtContent = "";

  for (var i = 0; i < captions.length; i++) {
    var cap = captions[i];

    srtContent += cap.index + "\n";
    srtContent += cap.timestamp + " --> " + cap.endTimestamp + "\n";
    srtContent += cap.text + "\n";
    srtContent += "\n";
  }

  try {
    var file = new File(outputPath);
    file.open("w");
    file.write(srtContent);
    file.close();

    return { success: true, file: outputPath, captions: captions.length };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

// ============================================================================
// EXPORT TO CSV
// ============================================================================

function exportToCSV(captions, outputPath) {
  /**
   * Export captions as CSV with metadata for Excel analysis
   */

  var csvContent = "Index,Start,End,Duration(s),Text,CharCount,WordCount\n";

  for (var i = 0; i < captions.length; i++) {
    var cap = captions[i];

    // Escape quotes and wrap text in quotes
    var text = cap.text.replace(/"/g, '""');

    csvContent += cap.index + ",";
    csvContent += cap.timestamp + ",";
    csvContent += cap.endTimestamp + ",";
    csvContent += cap.duration_sec.toFixed(3) + ",";
    csvContent += '"' + text + '",';
    csvContent += cap.textLength + ",";
    csvContent += cap.wordCount + "\n";
  }

  try {
    var file = new File(outputPath);
    file.open("w");
    file.write(csvContent);
    file.close();

    return { success: true, file: outputPath, captions: captions.length };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

// ============================================================================
// ORCHESTRATION
// ============================================================================

function exportCaptions(captions, seqName) {
  /**
   * Handle export file dialog and format selection
   */

  // Sanitize sequence name for filename
  var safeName = seqName.replace(/[^a-zA-Z0-9_-]/g, "_");

  // Default to Desktop or /tmp
  var defaultPath = new Folder(Folder.desktop.toString());
  if (!defaultPath.exists) {
    defaultPath = new Folder("/tmp");
  }

  // Export SRT
  var srtPath = defaultPath.toString() + "/" + safeName + "_captions.srt";
  var srtResult = exportToSRT(captions, srtPath);

  // Export CSV
  var csvPath = defaultPath.toString() + "/" + safeName + "_captions.csv";
  var csvResult = exportToCSV(captions, csvPath);

  var msg = "=== EXPORT RESULTS ===\n\n";

  if (srtResult.success) {
    msg += "✓ SRT exported: " + srtPath + "\n";
  } else {
    msg += "✗ SRT failed: " + srtResult.error + "\n";
  }

  if (csvResult.success) {
    msg += "✓ CSV exported: " + csvPath + "\n";
  } else {
    msg += "✗ CSV failed: " + csvResult.error + "\n";
  }

  msg += "\n=== END ===";

  alert(msg);
}

// ============================================================================
// EXECUTE
// ============================================================================

main();
