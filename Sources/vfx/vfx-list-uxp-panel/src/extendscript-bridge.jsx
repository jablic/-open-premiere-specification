/**
 * ExtendScript Bridge for MOGRT Text Editing
 * Runs inside Premiere Pro process with full DOM access
 * Handles sequential MOGRT text modification
 *
 * Called from UXP panel via messagebridge
 */

//@include "json2.js"

/**
 * Update MOGRT text for a single clip
 * Production-safe pattern with full error handling
 */
function updateMogrtTextDirect(trackIndex, clipIndex, newText) {
  try {
    const seq = app.project.activeSequence;
    if (!seq) {
      return { ok: false, err: "No active sequence" };
    }

    // Get track and clip
    const track = (trackIndex > 0 && trackIndex <= seq.videoTracks.length)
      ? seq.videoTracks[trackIndex - 1]
      : null;

    if (!track) {
      return { ok: false, err: `Track ${trackIndex} not found` };
    }

    const clip = (clipIndex > 0 && clipIndex <= track.clips.length)
      ? track.clips[clipIndex - 1]
      : null;

    if (!clip) {
      return { ok: false, err: `Clip ${clipIndex} not found on track ${trackIndex}` };
    }

    // Get MOGRT component
    const comp = clip.getMGTComponent ? clip.getMGTComponent() : null;
    if (!comp) {
      return {
        ok: false,
        err: `"${clip.name}" is not an AE-authored MOGRT or has no text component`
      };
    }

    // Find Source Text parameter
    let param = null;
    if (comp.properties.getParamForDisplayName) {
      param = comp.properties.getParamForDisplayName("Source Text")
            || comp.properties.getParamForDisplayName("Text");
    }

    if (!param) {
      return {
        ok: false,
        err: `MOGRT "${clip.name}" has no Source Text parameter exposed`
      };
    }

    // Get current value
    let raw = param.getValue();
    if (raw == null || raw === "") {
      return {
        ok: false,
        err: `"${clip.name}" Source Text is empty`
      };
    }

    // Parse JSON blob
    let blob;
    try {
      blob = JSON.parse(raw);
    } catch (e) {
      // Not JSON — Premiere-authored graphic or Legacy Title
      return {
        ok: false,
        err: `"${clip.name}" has non-JSON Source Text (Premiere-authored or Legacy Title?)`
      };
    }

    // Validate blob structure
    if (typeof blob !== 'object') {
      return {
        ok: false,
        err: `"${clip.name}" Source Text is not an object`
      };
    }

    // Store original for rollback
    const originalText = blob.textEditValue;

    // Mutate blob
    blob.textEditValue = String(newText);
    blob.fontTextRunLength = [String(newText).length]; // CRITICAL

    // Apply mutation
    param.setValue(JSON.stringify(blob), true);

    // Verify application (optional, adds overhead)
    const verifyRaw = param.getValue();
    let verifyBlob;
    try {
      verifyBlob = JSON.parse(verifyRaw);
    } catch (e) {
      // Verification failed
      return {
        ok: true,
        warning: `Updated but verification failed. Applied: "${newText}"`,
        originalText: originalText
      };
    }

    if (verifyBlob.textEditValue !== newText) {
      return {
        ok: false,
        err: `Verification failed: wrote "${newText}" but read back "${verifyBlob.textEditValue}"`
      };
    }

    return {
      ok: true,
      originalText: originalText,
      newText: newText,
      clipName: clip.name
    };
  } catch (e) {
    return {
      ok: false,
      err: `Exception: ${e.message || String(e)}`
    };
  }
}

/**
 * Batch update MOGRT texts sequentially
 * Updates spec: { track: number, clip: number, oldText: string, newText: string }[]
 */
function batchUpdateMogrtTexts(updateSpecs) {
  const results = [];
  let successCount = 0;
  let failCount = 0;

  for (let i = 0; i < updateSpecs.length; i++) {
    const spec = updateSpecs[i];
    const result = updateMogrtTextDirect(spec.track, spec.clip, spec.newText);

    results.push({
      index: i,
      spec: spec,
      result: result
    });

    if (result.ok) {
      successCount++;
    } else {
      failCount++;
    }
  }

  return {
    total: updateSpecs.length,
    successCount: successCount,
    failCount: failCount,
    results: results
  };
}

/**
 * Update captions sequentially
 * UXP native captions API is sufficient but include here for consistency
 */
function batchUpdateCaptions(captions, pattern) {
  const results = [];

  if (!app.project || !app.project.activeSequence) {
    return { ok: false, err: "No active sequence" };
  }

  const seq = app.project.activeSequence;

  try {
    // Captions in ExtendScript are limited, so this mainly documents the approach
    // Actual caption updates should happen via UXP API which is better supported

    return {
      ok: false,
      message: "Caption updates should use UXP native API (better supported)",
      details: "Captions are handled via UXP caption API, not ExtendScript"
    };
  } catch (e) {
    return {
      ok: false,
      err: `Exception: ${e.message || String(e)}`
    };
  }
}

/**
 * Main message handler
 * Receives commands from UXP panel via messaging
 */
const messageHandlers = {
  updateMogrtText: function(data) {
    return updateMogrtTextDirect(data.track, data.clip, data.newText);
  },

  batchUpdateMogrtTexts: function(data) {
    return batchUpdateMogrtTexts(data.updateSpecs);
  },

  batchUpdateCaptions: function(data) {
    return batchUpdateCaptions(data.captions, data.pattern);
  },

  ping: function(data) {
    return { ok: true, message: "ExtendScript bridge active" };
  }
};

/**
 * Listen for messages from UXP panel
 * Message format: { command: string, data: object }
 */
if (typeof addEventListener !== "undefined") {
  addEventListener("messageReceived", function(event) {
    try {
      const message = JSON.parse(event.data);
      const handler = messageHandlers[message.command];

      if (handler) {
        const result = handler(message.data || {});
        postMessage(JSON.stringify({
          id: message.id,
          command: message.command,
          result: result
        }));
      } else {
        postMessage(JSON.stringify({
          id: message.id,
          command: message.command,
          error: `Unknown command: ${message.command}`
        }));
      }
    } catch (e) {
      postMessage(JSON.stringify({
        error: `Script error: ${e.message || String(e)}`
      }));
    }
  });
}

// If called directly (for testing)
if (typeof updateMogrtTextDirect !== "undefined") {
  // Make functions available globally
  this.updateMogrtTextDirect = updateMogrtTextDirect;
  this.batchUpdateMogrtTexts = batchUpdateMogrtTexts;
}
