---
id: debugging
title: Debugging & Troubleshooting
category: reference
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: "14.0"
api_namespace: app
languages: [extendscript, uxp, javascript]
tags: [debugging, troubleshooting, errors, performance, logging, error-handling, qe-dom]
related: [extendscript-core, uxp, best-practices, cep, panels]
sources: [
  "Production experience",
  "Community findings",
  "Premiere 25.x testing"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Debugging & Troubleshooting

## TL;DR

**Debugging Premiere scripts:** ExtendScript Debugger (ESTK, old), UDT (UXP, modern), browser console (CEP). **Common errors:** Null references, async/await issues, version mismatches, file path problems.

---

## ExtendScript Debugging (Legacy)

### ExtendScript Toolkit (ESTK)

Old IDE for ES3 debugging. Deprecated.

```javascript
var seq = app.project.activeSequence;
if (!seq) {
  $.writeln("ERROR: No active sequence");
  $.quit();
}

$.writeln("Sequence: " + seq.name);
```

### Console Output

```javascript
$.writeln("Debug message");
$.writeln("Value: " + variable);
alert("Error: " + error.message);
```

---

## UXP Debugging (Modern)

### UDT (UXP Developer Tool)

```bash
npm install -g @adobe/udt
udt --watch ./plugin-folder
```

Features:
- Breakpoints
- Step-through execution
- Console logging
- Variable inspection
- Async/await debugging

---

## Error Handling & Diagnosis

### Null/Undefined Checks

**ExtendScript (Defensive):**
```javascript
// Always check before accessing
if (seq && seq.videoTracks && seq.videoTracks.length > 0) {
  var track = seq.videoTracks[0];
  var clip = track.clips[0];
  // Process clip
}
```

**UXP (Optional Chaining):**
```javascript
// Modern syntax (if supported)
const trackCount = await seq?.videoTracks?.length ?? 0;
const clip = await seq?.videoTracks?.[0]?.clips?.[0];
```

### Error Wrapping Pattern

**ExtendScript:**
```javascript
function safeSequenceOperation(func) {
  try {
    var seq = app.project.activeSequence;
    if (!seq) throw Error("No active sequence");
    
    return {
      success: true,
      result: func(seq)
    };
  } catch (e) {
    return {
      success: false,
      error: e.toString(),
      line: e.line,
      source: e.source
    };
  }
}

// Usage
var result = safeSequenceOperation(function(seq) {
  return seq.videoTracks.length;
});

if (!result.success) {
  $.writeln("Error at line " + result.line + ": " + result.error);
}
```

**UXP:**
```javascript
async function safeSequenceOperation(func) {
  try {
    const proj = await application.activeProject;
    if (!proj) throw new Error("No active project");
    
    const seq = await proj.activeSequence;
    if (!seq) throw new Error("No active sequence");
    
    const result = await func(seq);
    return { success: true, result };
  } catch (e) {
    console.error("Operation failed:", e.message);
    return { success: false, error: e.message };
  }
}

// Usage
const result = await safeSequenceOperation(async (seq) => {
  return await seq.videoTracks?.length ?? 0;
});
```

### Common Errors & Root Causes

| Error | Likely Cause | Diagnostic | Fix |
|---|---|---|---|
| "Cannot read property X of undefined" | Missing null check | Add console log before access | Check with `if (obj)` or `?.` |
| "TypeError: object is not iterable" | Trying to loop undefined array | Log `typeof array` | Ensure array exists and init if needed |
| "Promise not awaited" (UXP) | Missing `await` in async context | Check function is async | Add `await` or remove async if not needed |
| "File not found" | Cross-platform path issue | Log full path before File() call | Use Path.join() or normalize path |
| "No active sequence" | User hasn't opened sequence | Check at start of script | Alert user and exit gracefully |
| "Undo failed" | Mutation outside transaction | Check transaction wrapper | Wrap all mutations in `executeTransaction()` |
| "QE not available" | QE DOM not enabled | Check return value of enableQE() | Call `app.enableQE()` before accessing QE |
| "Invalid track index" | Array out of bounds | Log track count first | Add bounds check: `if (i < tracks.length)` |

---

## QE DOM Debugging (ExtendScript)

**Enable and Verify QE:**
```javascript
function verifyQEAvailable() {
  try {
    app.enableQE();
    var qeEvent = new QEEvent("test");
    $.writeln("QE is available");
    return true;
  } catch (e) {
    $.writeln("QE error: " + e.toString());
    return false;
  }
}

// Verify before using QE operations
if (verifyQEAvailable()) {
  // Use QE DOM safely
  var seq = app.project.activeSequence;
  if (seq) {
    var qeSeq = seq.getProjectMetadata();
  }
}
```

**QE Error Context:**
```javascript
function executeQEWithLogging(qeCommand) {
  $.writeln("QE Command: " + qeCommand);
  $.writeln("Active Project: " + (app.project ? app.project.name : "NONE"));
  $.writeln("Active Sequence: " + (app.project?.activeSequence?.name ?? "NONE"));
  
  try {
    var result = app.project.getProjectMetadata();
    $.writeln("QE Result: " + (result ? "Success" : "Null"));
    return result;
  } catch (e) {
    $.writeln("QE Error: " + e.toString());
    $.writeln("Error stack: " + (e.stack ?? "N/A"));
    return null;
  }
}
```

---

## Performance Profiling

### ExtendScript

```javascript
var start = new Date();
for (var i = 0; i < 1000; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
var end = new Date();
$.writeln("Time: " + (end - start) + "ms");
```

### UXP

```javascript
console.time("operation");
for (let i = 0; i < 1000; i++) {
  await processBatch(i);
}
console.timeEnd("operation");
```

---

## Logging & Inspection Patterns

### Structured Logging (ExtendScript)

```javascript
function log(level, message, data) {
  var timestamp = new Date().toISOString();
  var line = "[" + timestamp + "] " + level.toUpperCase() + ": " + message;
  
  if (data !== undefined) {
    line += " | " + JSON.stringify(data);
  }
  
  $.writeln(line);
  
  // Also write to file for persistence
  try {
    var logFile = new File("/tmp/premiere_debug.log");
    logFile.open("a");
    logFile.writeln(line);
    logFile.close();
  } catch (e) {
    // File I/O failed, continue with console only
  }
}

// Usage
log("info", "Sequence loaded", { name: seq.name, tracks: seq.videoTracks.length });
log("warn", "Offline media detected", { clipName: clip.name });
log("error", "Failed to relink", { error: e.toString(), clipName: clip.name });
```

### Object Inspector (UXP Async)

```javascript
async function inspectSequence(seq) {
  const result = {
    name: await seq?.name,
    id: await seq?.id,
    videoTracksCount: await seq?.videoTracks?.length,
    audioTracksCount: await seq?.audioTracks?.length,
    duration: await seq?.duration,
    timebase: await seq?.timebase,
    videoTrackData: []
  };
  
  if (seq && seq.videoTracks) {
    for (let i = 0; i < Math.min(3, await seq.videoTracks.length); i++) {
      const track = await seq.videoTracks[i];
      result.videoTrackData.push({
        index: i,
        clips: await track.clips?.length ?? 0
      });
    }
  }
  
  console.log("Sequence Inspection:", JSON.stringify(result, null, 2));
  return result;
}
```

---

## Debugging Workflow (Step-by-Step)

### 1. Identify Problem Scope

```javascript
// Is it a Premiere API issue or script logic?
if (!app.project) {
  $.writeln("SCOPE: Premiere not accessible - may be wrong context");
} else if (!app.project.activeSequence) {
  $.writeln("SCOPE: Sequence issue - check user selection");
} else {
  $.writeln("SCOPE: Script logic issue - trace execution");
}
```

### 2. Enable Detailed Logging

```javascript
function runWithDebug(func, debugLevel) {
  // debugLevel: 0=off, 1=errors, 2=warnings, 3=all
  var DEBUG = debugLevel || 3;
  
  function debug(msg, level) {
    if (level <= DEBUG) $.writeln("[D" + level + "] " + msg);
  }
  
  try {
    debug("Start execution", 3);
    debug("Project: " + app.project.name, 3);
    
    var result = func(debug);
    
    debug("Result: " + JSON.stringify(result), 3);
    return result;
  } catch (e) {
    debug("EXCEPTION: " + e.toString(), 1);
    debug("at " + e.fileName + ":" + e.line, 1);
  }
}

// Usage
runWithDebug(function(debug) {
  debug("Processing started", 3);
  // Your code here
}, 3);
```

### 3. Isolate Variable State

```javascript
function traceExecution(seq) {
  $.writeln("=== TRACE START ===");
  $.writeln("seq exists: " + (seq ? "yes" : "NO"));
  $.writeln("seq.name: " + (seq?.name ?? "undefined"));
  $.writeln("seq.videoTracks: " + (seq?.videoTracks ? "exists" : "NO"));
  
  if (seq && seq.videoTracks) {
    $.writeln("track count: " + seq.videoTracks.length);
    
    for (var i = 0; i < seq.videoTracks.length; i++) {
      var track = seq.videoTracks[i];
      $.writeln("  Track[" + i + "].clips: " + track.clips.length);
    }
  }
  $.writeln("=== TRACE END ===");
}
```

---

## See Also

- Knowledge/best-practices.md — Error handling strategies
- Knowledge/extendscript-core.md — ExtendScript runtime specifics
- Knowledge/uxp.md — UXP async debugging patterns

---

## Sources

- ExtendScript Debugger: https://ppro-scripting.docsforadobe.dev/
- UDT: https://github.com/Adobe-UXP/UDT
- Adobe Debugging Guide: https://support.adobe.com/en-us/HT208197
