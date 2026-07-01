/**
 * Batch Marker Creation from JSON
 *
 * Runtime: ExtendScript (ES3) for Premiere Pro 14.x–25.x
 *
 * Purpose:
 * - Programmatically create timeline markers with colors and metadata
 * - Import marker specs from JSON or hardcoded array
 * - Safe error handling with per-marker logging
 *
 * Topic doc: markers-and-annotations.md
 */

// ============================================================================
// MAIN: Batch create markers on active sequence
// ============================================================================

function main() {
  var seq = app.project.activeSequence;
  if (!seq) {
    alert("ERROR: No active sequence. Please open a sequence first.");
    return;
  }

  // Sample marker specifications
  // Format: { time_sec, text, type_idx (0-7), metadata (optional) }
  var markerSpecs = [
    {
      time_sec: 1.5,
      text: "VFX: Explosion effect",
      type_idx: 3,  // orange
      metadata: { vfx_id: "VFX-001", priority: "high", artist: "john" }
    },
    {
      time_sec: 5.2,
      text: "Grade: Color temp 5000K",
      type_idx: 2,  // red-orange
      metadata: { grade_id: "GRD-001", lut: "Rec709" }
    },
    {
      time_sec: 12.0,
      text: "Audio: Sync checkpoint",
      type_idx: 6,  // cyan
      metadata: { sync_frame: 288 }
    },
    {
      time_sec: 18.75,
      text: "Approved by client",
      type_idx: 5,  // green
      metadata: { status: "approved", date: "2026-07-01" }
    }
  ];

  var result = batchCreateMarkers(seq, markerSpecs);

  // Summary
  var summary = "Batch Marker Creation Summary\n" +
    "==============================\n" +
    "Sequence: " + seq.name + "\n" +
    "Total specs: " + result.total + "\n" +
    "Created: " + result.created + "\n" +
    "Failed: " + result.failed + "\n\n" +
    result.log.join("\n");

  alert(summary);
  $.writeln(summary);  // Also log to console
}

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Create multiple markers on a sequence from specifications
 *
 * @param {Sequence} sequence - Target Premiere sequence
 * @param {Array} markerSpecs - Array of marker specifications
 * @returns {Object} { total, created, failed, log }
 */
function batchCreateMarkers(sequence, markerSpecs) {
  if (!sequence || !sequence.markers) {
    return { total: 0, created: 0, failed: 0, log: ["ERROR: Invalid sequence"] };
  }

  var log = [];
  var created = 0, failed = 0;

  log.push("Starting batch marker creation...");

  for (var i = 0; i < markerSpecs.length; i++) {
    var spec = markerSpecs[i];

    // Validate spec
    if (!spec.time_sec || spec.time_sec < 0) {
      log.push("[" + i + "] SKIP: Invalid time: " + spec.time_sec);
      failed++;
      continue;
    }

    try {
      // Create marker at specified time (in seconds)
      var marker = sequence.markers.createMarker(spec.time_sec);

      // Set marker properties
      marker.name = sanitizeText(spec.text || ("Marker " + (i + 1)));
      marker.type = clampMarkerType(spec.type_idx || 4);  // default to yellow

      // Store metadata as JSON in comments field
      if (spec.metadata) {
        marker.comments = JSON.stringify(spec.metadata);
      }

      log.push("[" + i + "] OK: Created at " + formatSeconds(spec.time_sec) +
               " | '" + marker.name + "' | color=" + getMarkerColorName(marker.type));
      created++;

    } catch (e) {
      log.push("[" + i + "] ERROR: " + e.toString());
      failed++;
    }
  }

  log.push("\nBatch complete: " + created + " created, " + failed + " failed");

  return {
    total: markerSpecs.length,
    created: created,
    failed: failed,
    log: log
  };
}

/**
 * Sanitize marker text (remove special chars that break display)
 */
function sanitizeText(text) {
  return String(text)
    .replace(/[\n\r]/g, " ")      // newlines to spaces
    .substring(0, 256);            // Premiere limit
}

/**
 * Clamp marker type to valid range 0–7
 */
function clampMarkerType(type) {
  var t = parseInt(type) || 4;
  return Math.max(0, Math.min(7, t));
}

/**
 * Get human-readable color name for marker type index
 */
function getMarkerColorName(typeIdx) {
  var colors = ["Red", "Pink", "Red-Orange", "Orange", "Yellow", "Green", "Cyan", "Blue"];
  return colors[typeIdx] || "Unknown";
}

/**
 * Format seconds as HH:MM:SS.ms
 */
function formatSeconds(seconds) {
  var h = Math.floor(seconds / 3600);
  var m = Math.floor((seconds % 3600) / 60);
  var s = Math.floor(seconds % 60);
  var ms = Math.round((seconds % 1) * 1000);

  return (h < 10 ? "0" : "") + h + ":" +
         (m < 10 ? "0" : "") + m + ":" +
         (s < 10 ? "0" : "") + s + "." +
         (ms < 100 ? (ms < 10 ? "00" : "0") : "") + ms;
}

/**
 * Read markers from sequence and export to CSV
 */
function exportMarkersToCSV(sequence, outputPath) {
  if (!sequence || !sequence.markers) {
    alert("ERROR: Invalid sequence");
    return false;
  }

  var csv = "Index,Timecode,Text,Color,Metadata\n";
  var markers = sequence.markers;

  for (var i = 0; i < markers.numMarkers; i++) {
    var marker = markers[i];
    var timecode = formatSeconds(marker.start.seconds);
    var color = getMarkerColorName(marker.type);
    var text = (marker.name || "").replace(/,/g, ";");  // escape commas
    var metadata = (marker.comments || "").replace(/,/g, ";").replace(/\n/g, " ");

    csv += i + "," + timecode + ",\"" + text + "\"," + color + ",\"" + metadata + "\"\n";
  }

  // Write to file
  try {
    var file = new File(outputPath);
    file.open("w");
    file.write(csv);
    file.close();
    alert("Exported " + markers.numMarkers + " markers to:\n" + outputPath);
    return true;
  } catch (e) {
    alert("ERROR exporting to file: " + e.toString());
    return false;
  }
}

// ============================================================================
// EXECUTE
// ============================================================================

main();
