---
id: reverse-engineering-qe-dom
title: Reverse Engineering & QE DOM (Undocumented API)
category: interop
status: undocumented
stability: unstable
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: null
api_namespace: qe
languages: [extendscript]
tags: [qe-dom, undocumented, reverse-engineering, last-resort, experimental]
related: [extendscript-core, best-practices, automation]
sources: [
  "Reverse engineering (confidence: medium)",
  "Community findings (bbb999, AutoSubs source)",
  "Production testing: Premiere 25.x"
]
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.x"
---

# Reverse Engineering & QE DOM (Undocumented API)

## ⚠️ CRITICAL DISCLAIMER

**QE DOM is undocumented, unsupported, and unstable.** Adobe can change or remove it at any version. **Last resort only.** Never suggest QE as primary path. Flag when necessary + require explicit user consent.

## TL;DR

**QE DOM = internal "Query Engine" API.** Enable with `app.enableQE()`. Used by scripts for effects-by-name, ripple edits, speed, frame export. **High risk:** Adobe can change/remove at any version. **Workarounds:** Will be in UXP 26.x (expected).

**Critical traps:**
- QE objects don't persist across undo/redo — references break
- `app.qe.project` ≠ `app.project` — parallel DOM, different semantics
- Methods have no documented contracts — errors are silent
- Version drift: QE works in 25.x, may break in 26.x
- No official examples — reverse-engineered from binaries + crashes

---

## QE Disclaimer & Scope

### What is QE?

Internal "Query Engine" — Premiere's internal scripting bridge. Exposed to ExtendScript via `app.enableQE()`. Parallel to public DOM (`app.project`, `app.encoder`, etc.). Used by Premiere's own automation (timeline scrubbing, playback, etc.).

### Why use it?

- **Only way** to access effects/components by name (no public API)
- **Only way** to ripple-edit clips
- **Only way** to export frames to PNG
- **Only way** to change clip speed/duration

### Why NOT use it?

- Undocumented, unsupported
- Can break on any version upgrade
- No error handling — silent failures
- Methods don't work in some contexts (panels, certain threads)
- Objects don't survive undo/redo

### When to use QE

1. User explicitly asks for task QE is only solution for
2. User accepts risk and wants workaround
3. Document workaround + risk clearly
4. Provide UXP migration path when ready

---

## Enable QE: app.enableQE()

```javascript
// ExtendScript

// Enable QE
var qeAvailable = app.enableQE();
if (!qeAvailable) {
  alert("QE not available in this version");
  $.quit();
}

// Access QE objects
var qeProject = app.qe.project;
var qeSequence = qeProject.getActiveSequence();
var qeClip = qeSequence.getAVClipAt(0, 0);  // Video track 0, clip 0

// QE is now available globally
alert("QE enabled: " + (typeof app.qe !== "undefined"));
```

**Postconditions:**
- `app.qe` becomes available
- `app.qe.project` exists (may differ from `app.project`)
- QE methods callable (with caveats)

---

## QE Object Hierarchy
**Critical:** QEClip ≠ TrackItem. QEClip is timeline-aware; TrackItem is not.

---

## Effects-by-Name (Only Way in ExtendScript)

```javascript
app.enableQE();

var qeClip = app.qe.project.getActiveSequence()
  .getAVClipAt(0, 0);  // Video track 0, clip 0

// Find effect by name
var effectName = "Lumetri Color";
var lumetriComponent = null;

for (var i = 0; i < qeClip.getNumComponents(); i++) {
  var comp = qeClip.getComponentAt(i);
  var compName = comp.getName();
  if (compName === effectName) {
    lumetriComponent = comp;
    break;
  }
}

if (!lumetriComponent) {
  alert("Effect not found: " + effectName);
  $.quit();
}

// Read/write parameters (undocumented IDs)
for (var p = 0; p < lumetriComponent.getNumProperties(); p++) {
  var prop = lumetriComponent.getProperty(p);
  var propName = prop.getDisplayName();
  
  if (propName.indexOf("Saturation") !== -1) {
    prop.setValue(1.5);  // 150%
  }
}
```

**Gotcha:** Parameter names vary by Premiere version, plugin version, localization. Script must be robust to name changes.

---

## Ripple Edits (QE Only)

```javascript
app.enableQE();

var qeSeq = app.qe.project.getActiveSequence();
var qeClip = qeSeq.getAVClipAt(0, 0);  // First clip, video track 0

// Delete with ripple (shifts remaining clips to fill gap)
// Public ExtendScript has no ripple-delete; QE only
qeClip.rippleDelete();
```

**Risk:** If QE's ripple method changes in Premiere 26+, this breaks silently.

---

## Speed / Duration (QE Only)

```javascript
app.enableQE();

var qeClip = app.qe.project.getActiveSequence()
  .getAVClipAt(0, 0);

// Get current speed (relative to sequence frame rate)
var currentSpeed = qeClip.getSpeed();  // 1.0 = normal
alert("Current speed: " + currentSpeed);

// Set to 50% speed (slow-motion)
qeClip.setSpeed(0.5);

// Set to 200% speed (fast-motion)
qeClip.setSpeed(2.0);
```

**Gotcha:** QE speed is relative to sequence frame rate, not absolute.

---

## Frame Export (QE Only)

```javascript
app.enableQE();

var qeSeq = app.qe.project.getActiveSequence();

// Get current playhead position (in ticks)
var playheadTicks = qeSeq.getPlayheadPosition();

// Export frame at playhead
var outputPath = "/tmp/frame.png";
qeSeq.exportFramePNG(playheadTicks, outputPath);

alert("Frame exported to: " + outputPath);
```

**Limitation:** No bitmap data returned; file output only. No control over resolution, codec, or color space.

---

## Common QE Errors

| Error | Cause | Workaround |
|---|---|---|
| `app.qe is undefined` | `enableQE()` not called or failed | Ensure `app.enableQE()` returns true |
| Silent failure (no error) | QE method not supported in context | Wrap in try/catch + logging |
| QE references break after undo | QE objects don't persist | Re-fetch objects after undo |
| getComponentByName returns null | Effect not applied to clip | Verify effect exists in public DOM first |
| Speed changes don't appear | Changes in QE not reflected in UI | Force UI refresh; may require undo/redo |

---

## Confidence Matrix

| Feature | Confidence | Tested In | Risk |
|---|---|---|---|
| `app.enableQE()` | High | 24.x, 25.x | Low — fundamental |
| effects-by-name | Medium | 25.x, scripts | Medium — effect renames |
| ripple edits | Medium | 25.x | High — complex logic |
| speed/duration | Medium | 25.x | High — may move to UXP |
| frame export | Medium | 25.x | High — may move to UXP |
| QE in panels | Low | Anecdotal | Very high — thread context |

---

## UXP Migration Timeline

| Feature | Premiere 25.6 | 26.x (Expected) |
|---|---|---|
| effects-by-name | ❌ | Likely ✅ |
| ripple edits | ❌ | Likely ✅ |
|
cat > Examples/extendscript/cep-bridge-safe.jsx << 'EOF'
/**
 * CEP Panel Safety Bridge (ExtendScript)
 * 
 * Safe wrapper for CEP <-> ExtendScript communication with error handling.
 * Meant to be invoked FROM CEP panel via CSInterface.evalScript()
 * 
 * Usage (from CEP JavaScript):
 *   csInterface.evalScript(
 *     'var bridgeResult = ' + jsxCode + '; bridgeResult;',
 *     callback
 *   );
 */

(function() {
  'use strict';

  // CEP Bridge Utilities
  var CEPBridge = {
    /**
     * Safe project getter with error wrapping
     */
    getActiveProject: function() {
      if (!app || !app.project) {
        return { error: "Premiere not available" };
      }
      try {
        return {
          name: app.project.name,
          path: app.project.path,
          isValid: app.project.isValid
        };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * List all sequences with safe iteration
     */
    listSequences: function() {
      if (!app || !app.project) {
        return { error: "No project" };
      }
      
      var sequences = [];
      try {
        var numSeqs = app.project.sequences.numSequences;
        for (var i = 0; i < numSeqs; i++) {
          var seq = app.project.sequences[i];
          sequences.push({
            index: i,
            name: seq.name,
            duration: seq.duration.seconds,
            videoTracks: seq.videoTracks.numTracks,
            audioTracks: seq.audioTracks.numTracks
          });
        }
        return { sequences: sequences };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * Get active sequence metadata
     */
    getActiveSequence: function() {
      if (!app || !app.project) {
        return { error: "No project" };
      }
      
      try {
        var seq = app.project.activeSequence;
        if (!seq) {
          return { error: "No active sequence" };
        }
        
        return {
          name: seq.name,
          framerate: seq.frameRate,
          duration: seq.duration.seconds,
          pixelAspectRatio: seq.pixelAspectRatio,
          videoTracks: seq.videoTracks.numTracks,
          audioTracks: seq.audioTracks.numTracks
        };
      } catch (e) {
        return { error: e.toString() };
      }
    },

    /**
     * Get footer text (safe read)
     */
    getFooterText: function(index) {
      if (!app || !app.project) {
        return { error: "No project" };
      }
      
      try {
        var text = app.project.getFooterText(index);
        return { text: text };
      } catch (e) {
        return { error: e.toString() };
      }
    }
  };

  // Execute requested command
  // Called as: var result = new CBridge().call('listSequences');
  function Bridge(methodName) {
    this.methodName = methodName;
  }

  Bridge.prototype.call = function() {
    if (CEPBridge[this.methodName]) {
      return CEPBridge[this.methodName].apply(null, arguments);
    }
    return { error: "Method not found: " + this.methodName };
  };

  // Return JSON-serializable result
  // CEP will receive this as string; parse with JSON.parse()
  return JSON.stringify({
    status: "ready",
    available: Object.keys(CEPBridge),
    methods: {
      getActiveProject: "Returns project name, path, validity",
      listSequences: "Returns array of all sequences with metadata",
      getActiveSequence: "Returns active sequence metadata",
      getFooterText: "Returns footer text by index"
    }
  });
})();
