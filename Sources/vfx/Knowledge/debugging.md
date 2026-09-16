---
id: debugging
title: Debugging & Troubleshooting
category: reference
status: current
stability: active
doc_status: partial
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [extendscript, uxp, javascript]
tags: [debugging, troubleshooting, errors, performance]
related: [extendscript-core, uxp, best-practices, cep]
sources: [
  "Production experience",
  "Community findings"
]
confidence: medium
last_verified: "2026-06-30"
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

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| "Cannot read property X of undefined" | Object is null | Check preconditions |
| "Promise not awaited" | Forgot `await` | Add `await` to async call |
| "File not found" | Path broken cross-platform | Use `Path.join()` |
| "Undo failed" | Mutation outside transaction | Wrap in `executeTransaction()` |
| "QE not available" | `enableQE()` not called | Call `app.enableQE()` first |

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

## Sources

- ExtendScript Debugger: https://ppro-scripting.docsforadobe.dev/
- UDT: https://github.com/Adobe-UXP/UDT
