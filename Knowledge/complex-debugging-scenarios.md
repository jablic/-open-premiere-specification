---
id: complex-debugging-scenarios
title: Complex Debugging Scenarios & Forensics
category: advanced
status: current
stability: active
doc_status: complete
introduced: "Premiere Pro CC 2015"
min_premiere_version: "14.0"
api_namespace: null
languages: [extendscript, javascript, jsx, python, shell]
tags: [debugging, troubleshooting, forensics, memory-leaks, performance, error-recovery, logging]
related: [debugging, performance-profiling-guide, best-practices, faq-troubleshooting-tree]
sources: [
  "Advanced debugging techniques",
  "Memory forensics patterns",
  "Production issue diagnosis",
  "Real-world debugging case studies"
]
confidence: high
last_verified: "2026-07-01"
verified_against_version: "25.6"
---

# Complex Debugging Scenarios & Forensics

## TL;DR

**Memory Leaks:** Profile heap; identify unreleased objects; check for circular refs. **Hang/Freeze:** Trace thread stalls via performance profiler; find blocking operations (I/O, API calls). **Intermittent Failures:** Reproduce with minimal repro case; add detailed logging; check race conditions. **Silent Failures:** Hook into error handlers; intercept uncaught exceptions; log state before/after. **Performance Regression:** Baseline before/after; profile hot paths; check dependency updates. **Data Corruption:** Verify input data; trace mutation points; add checksums/validation. **Plugin Crashes:** Catch C++ exceptions in bridge; add try-catch at API boundaries; log stack traces.

---

## Memory Leak Detection & Diagnosis

### Identify and Fix Memory Leaks

```javascript
function diagnoseMemoryLeak() {
  /**
   * Detect and diagnose memory leaks in Premiere plugin
   * Symptoms: Plugin memory grows over time, never released
   */
  
  $.writeln("=== MEMORY LEAK DIAGNOSIS ===\n");
  
  $.writeln("Symptoms:");
  $.writeln("- Plugin memory grows every time feature is used");
  $.writeln("- Memory never decreases (even after disabling feature)");
  $.writeln("- Eventually Premiere becomes slow, then crashes");
  $.writeln("- After restart, memory resets (confirms plugin is issue)");
  $.writeln("");
  
  $.writeln("Root Causes (Common):");
  $.writeln("1. Circular References");
  $.writeln("   Problem: A holds ref to B, B holds ref to A");
  $.writeln("   Garbage collector can't free (both in-use)");
  $.writeln("   Solution: Break cycle before discard");
  $.writeln("");
  
  $.writeln("2. Global Variable Accumulation");
  $.writeln("   Problem: globalArray.push(largeObject)  // Every call");
  $.writeln("   Never cleared → array grows infinitely");
  $.writeln("   Solution: Clear array on feature disable");
  $.writeln("");
  
  $.writeln("3. Event Listener Leaks");
  $.writeln("   Problem: app.onClose += function() {}  // No remove");
  $.writeln("   Handler registered but never unregistered");
  $.writeln("   Solution: Store ref, call removeFunction()");
  $.writeln("");
  
  $.writeln("4. Unclosed File Handles");
  $.writeln("   Problem: var f = new File(path);");
  $.writeln("           f.open('r');  // Never closed");
  $.writeln("   Solution: f.close(); in finally block");
  $.writeln("");
  
  $.writeln("5. Cached DOM References");
  $.writeln("   Problem: var panel = app.panels.find(...); // Cache");
  $.writeln("           If panel removed, ref still held");
  $.writeln("   Solution: Validate ref before use, clear on destroy");
  $.writeln("");
  
  $.writeln("Diagnosis Workflow:");
  $.writeln("1. Monitor memory over time:");
  $.writeln("   - Activity Monitor (Mac) / Task Manager (Windows)");
  $.writeln("   - Record memory every 5 min for 1 hour");
  $.writeln("   - If monotonically increasing = likely leak");
  $.writeln("");
  $.writeln("2. Isolate the leak:");
  $.writeln("   - Enable/disable features one by one");
  $.writeln("   - Find which feature causes growth");
  $.writeln("   - Reproduce with minimal code");
  $.writeln("");
  $.writeln("3. Add detailed logging:");
  $.writeln("   - Log object creation/destruction");
  $.writeln("   - Log when arrays/maps modified");
  $.writeln("   - Track total count of objects");
  $.writeln("");
  $.writeln("4. Use profiler (if available):");
  $.writeln("   - Node.js heap snapshot");
  $.writeln("   - Chrome DevTools memory profiler");
  $.writeln("   - Export heap dump, search for suspects");
  $.writeln("");
  $.writeln("5. Fix and verify:");
  $.writeln("   - Apply fix (break cycle, clear array, etc)");
  $.writeln("   - Re-run memory test");
  $.writeln("   - Confirm memory stable over time");
  
  return { detectionMethod: "memory-monitoring", fixStrategy: "identify-retention" };
}

// Usage
diagnoseMemoryLeak();
```

### Memory Leak Code Patterns

```javascript
function memoryLeakPatterns() {
  /**
   * Common memory leak code patterns and fixes
   */
  
  $.writeln("=== MEMORY LEAK CODE PATTERNS ===\n");
  
  $.writeln("LEAK 1: Circular Reference");
  $.writeln("❌ LEAK:");
  $.writeln("var obj1 = {};");
  $.writeln("var obj2 = {};");
  $.writeln("obj1.ref = obj2;  // obj1 → obj2");
  $.writeln("obj2.ref = obj1;  // obj2 → obj1 (CYCLE!)");
  $.writeln("obj1 = null;  // obj1 released but obj2 still held");
  $.writeln("obj2 = null;  // obj2 released but obj1 in memory");
  $.writeln("");
  $.writeln("✓ FIX:");
  $.writeln("obj1.ref = null;  // Break cycle before release");
  $.writeln("obj2.ref = null;");
  $.writeln("obj1 = null;");
  $.writeln("obj2 = null;");
  $.writeln("");
  
  $.writeln("LEAK 2: Global Array Growth");
  $.writeln("❌ LEAK:");
  $.writeln("var globalCache = [];");
  $.writeln("function processItem(item) {");
  $.writeln("  globalCache.push(item);  // Growing every call");
  $.writeln("}");
  $.writeln("// Cache never cleared → memory grows");
  $.writeln("");
  $.writeln("✓ FIX:");
  $.writeln("function processItem(item) {");
  $.writeln("  var localCache = [item];  // Local scope");
  $.writeln("  // ... use localCache ...");
  $.writeln("}  // localCache freed when function ends");
  $.writeln("");
  
  $.writeln("LEAK 3: Event Listener Not Removed");
  $.writeln("❌ LEAK:");
  $.writeln("function setupPanel() {");
  $.writeln("  app.onClose += function() {");
  $.writeln("    // Handler registered but never removed");
  $.writeln("  };");
  $.writeln("}");
  $.writeln("");
  $.writeln("✓ FIX:");
  $.writeln("var closeHandler = function() { };");
  $.writeln("app.onClose += closeHandler;");
  $.writeln("// Later: app.onClose -= closeHandler;");
  $.writeln("");
  
  $.writeln("LEAK 4: Unclosed File Handle");
  $.writeln("❌ LEAK:");
  $.writeln("function readFile(path) {");
  $.writeln("  var f = new File(path);");
  $.writeln("  f.open('r');");
  $.writeln("  var content = f.read();");
  $.writeln("  // Forgot f.close()");
  $.writeln("}");
  $.writeln("");
  $.writeln("✓ FIX:");
  $.writeln("function readFile(path) {");
  $.writeln("  var f = new File(path);");
  $.writeln("  try {");
  $.writeln("    f.open('r');");
  $.writeln("    return f.read();");
  $.writeln("  } finally {");
  $.writeln("    f.close();  // Always executed");
  $.writeln("  }");
  $.writeln("}");
  $.writeln("");
  
  $.writeln("LEAK 5: Cached DOM Reference After Removal");
  $.writeln("❌ LEAK:");
  $.writeln("var panel = app.panels.find('MyPanel');");
  $.writeln("// If panel removed from UI, reference still held");
  $.writeln("");
  $.writeln("✓ FIX:");
  $.writeln("var panelRef = null;");
  $.writeln("function getPanel() {");
  $.writeln("  if (!panelRef || !panelRef.isValid) {");
  $.writeln("    panelRef = app.panels.find('MyPanel');");
  $.writeln("  }");
  $.writeln("  return panelRef;");
  $.writeln("}");
  
  return { leaksIdentified: 5, fixed: 5 };
}

// Usage
memoryLeakPatterns();
```

---

## Hang/Freeze Investigation

### Diagnose Frozen UI

```javascript
function diagnoseUIFreeze() {
  /**
   * Identify why Premiere UI becomes unresponsive
   */
  
  $.writeln("=== UI FREEZE DIAGNOSIS ===\n");
  
  $.writeln("Symptoms:");
  $.writeln("- UI stops responding to clicks");
  $.writeln("- Progress bar stuck (not updating)");
  $.writeln("- Keyboard input ignored");
  $.writeln("- Can force-quit Premiere (not completely hung)");
  $.writeln("");
  
  $.writeln("Root Causes (Most Common):");
  $.writeln("1. Blocking I/O on Main Thread");
  $.writeln("   - File read/write without async");
  $.writeln("   - Network call (API) without timeout");
  $.writeln("   - Database query without background worker");
  $.writeln("   → Solution: Use async, move to background thread");
  $.writeln("");
  
  $.writeln("2. Infinite Loop / Runaway Code");
  $.writeln("   - while(true) { } (no exit condition)");
  $.writeln("   - Recursion without base case");
  $.writeln("   - O(n²) or worse algorithm on large data");
  $.writeln("   → Solution: Add timeouts, break conditions");
  $.writeln("");
  
  $.writeln("3. Synchronous Rendering");
  $.writeln("   - Updating 10,000+ UI elements in loop");
  $.writeln("   - Re-rendering on every keystroke");
  $.writeln("   - No throttle/debounce on rapid events");
  $.writeln("   → Solution: Batch updates, throttle events");
  $.writeln("");
  
  $.writeln("4. Deadlock / Waiting");
  $.writeln("   - Thread A holds lock, waits for Thread B");
  $.writeln("   - Thread B waiting for Thread A to release");
  $.writeln("   → Solution: Avoid nested locks, use timeout");
  $.writeln("");
  
  $.writeln("Diagnosis Steps:");
  $.writeln("1. Identify exact action that causes freeze");
  $.writeln("   - Screenshot exact state");
  $.writeln("   - Note exact steps to reproduce");
  $.writeln("");
  $.writeln("2. Check system resources while frozen");
  $.writeln("   - CPU usage: High (>50%) = heavy computation");
  $.writeln("   - CPU usage: Low (<10%) = likely I/O wait");
  $.writeln("   - Disk activity: Yes = I/O blocking");
  $.writeln("   - Network activity: Yes = API call blocking");
  $.writeln("");
  $.writeln("3. Add debug timing:");
  $.writeln("   var start = new Date().getTime();");
  $.writeln("   // ... operation ...");
  $.writeln("   var elapsed = new Date().getTime() - start;");
  $.writeln("   $.writeln('Duration: ' + elapsed + 'ms');");
  $.writeln("");
  $.writeln("4. If operation takes > 500ms:");
  $.writeln("   - Move to background thread (Worker)");
  $.writeln("   - Show progress indicator");
  $.writeln("   - Allow user to cancel");
  $.writeln("");
  $.writeln("5. Verify fix:");
  $.writeln("   - UI responsive during operation");
  $.writeln("   - Progress shows continuously");
  $.writeln("   - User can cancel / abort");
  
  return { cause: "blocking-operation", solution: "async-background-worker" };
}

// Usage
diagnoseUIFreeze();
```

---

## Intermittent Failure Investigation

### Debug Race Conditions

```javascript
function debugRaceCondition() {
  /**
   * Diagnose and fix intermittent/race condition failures
   */
  
  $.writeln("=== RACE CONDITION DEBUGGING ===\n");
  
  $.writeln("Symptoms:");
  $.writeln("- Works sometimes, fails other times (unpredictable)");
  $.writeln("- Fails under heavy load, passes when idle");
  $.writeln("- Different results on different machines");
  $.writeln("- Timing-dependent (fails if fast, passes if slow)");
  $.writeln("");
  
  $.writeln("Root Causes:");
  $.writeln("1. Async Operations in Wrong Order");
  $.writeln("   Problem:");
  $.writeln("   initA();  // Async (no wait)");
  $.writeln("   useA();   // Uses A (but A not ready yet!)");
  $.writeln("   Solution: Chain with callback or Promise");
  $.writeln("");
  $.writeln("2. Shared State Modification");
  $.writeln("   Problem:");
  $.writeln("   Thread A: globalVar = 5;");
  $.writeln("   Thread B: globalVar = 10;");
  $.writeln("   Thread A: use(globalVar);  // Which value?");
  $.writeln("   Solution: Use local vars, atomic operations");
  $.writeln("");
  $.writeln("3. Missing Synchronization");
  $.writeln("   Problem:");
  $.writeln("   if (array.length > 0) {  // Check");
  $.writeln("     var item = array.pop();  // Modify (race!)");
  $.writeln("   }");
  $.writeln("   // Between check & modify, another thread empties array");
  $.writeln("   Solution: Atomic check-and-modify");
  $.writeln("");
  
  $.writeln("Reproduction Technique:");
  $.writeln("1. Add random delays (to expose race):");
  $.writeln("   setTimeout(function() { }, Math.random() * 100);");
  $.writeln("");
  $.writeln("2. Stress test (heavy load):");
  $.writeln("   - Run operation 1000 times");
  $.writeln("   - Open many concurrent operations");
  $.writeln("   - Force garbage collection between ops");
  $.writeln("");
  $.writeln("3. Detailed logging:");
  $.writeln("   - Log every state change with timestamp");
  $.writeln("   - Timestamp format: ms precision");
  $.writeln("   - Look for out-of-order events");
  $.writeln("");
  $.writeln("4. Add assertions:");
  $.writeln("   if (state !== EXPECTED_STATE) {");
  $.writeln("     throw Error('State mismatch at operation X');");
  $.writeln("   }");
  $.writeln("");
  
  $.writeln("Fix Patterns:");
  $.writeln("✓ Use callbacks/Promises for async ordering");
  $.writeln("✓ Avoid global state (use local variables)");
  $.writeln("✓ Atomic operations (check-and-modify together)");
  $.writeln("✓ Queue operations (sequential, not parallel)");
  $.writeln("✓ Add explicit synchronization (locks, mutexes)");
  
  return { detectionMethod: "stress-test-with-logging", fixStrategy: "async-chaining" };
}

// Usage
debugRaceCondition();
```

---

## Silent Failure Recovery

### Catch and Log Uncaught Exceptions

```javascript
function catchSilentFailures() {
  /**
   * Intercept failures that silently fail (no error message)
   */
  
  $.writeln("=== SILENT FAILURE DETECTION ===\n");
  
  $.writeln("Setup Global Error Handler:");
  $.writeln("$.onError = function(error) {");
  $.writeln("  // Catch all uncaught errors");
  $.writeln("  logError({");
  $.writeln("    message: error.message,");
  $.writeln("    stack: error.stack,");
  $.writeln("    time: new Date().toISOString(),");
  $.writeln("    source: error.source,");
  $.writeln("    line: error.line");
  $.writeln("  });");
  $.writeln("  return true;  // Suppress error (prevent Premiere crash)");
  $.writeln("};");
  $.writeln("");
  
  $.writeln("Add try-catch at API Boundaries:");
  $.writeln("function callExternalAPI(url) {");
  $.writeln("  try {");
  $.writeln("    var result = $.getenv('API_RESULT');");
  $.writeln("    return result;");
  $.writeln("  } catch (e) {");
  $.writeln("    logError({");
  $.writeln("      context: 'callExternalAPI',");
  $.writeln("      url: url,");
  $.writeln("      error: e.toString()");
  $.writeln("    });");
  $.writeln("    return null;  // Graceful failure");
  $.writeln("  }");
  $.writeln("}");
  $.writeln("");
  
  $.writeln("State Snapshot Before Risky Operation:");
  $.writeln("var snapshot = {");
  $.writeln("  time: new Date().toISOString(),");
  $.writeln("  activePanels: app.panels.length,");
  $.writeln("  activeProject: app.project.name,");
  $.writeln("  selectedClips: getSelectedClips(),");
  $.writeln("  memory: getMemoryUsage()");
  $.writeln("};");
  $.writeln("");
  $.writeln("try {");
  $.writeln("  riskyOperation();");
  $.writeln("} catch (e) {");
  $.writeln("  logError({");
  $.writeln("    snapshotBefore: snapshot,");
  $.writeln("    operation: 'riskyOperation',");
  $.writeln("    error: e.toString()");
  $.writeln("  });");
  $.writeln("}");
  $.writeln("");
  
  $.writeln("Log to File (for later analysis):");
  $.writeln("function logError(errorObject) {");
  $.writeln("  var logFile = new File(Folder.userData.absoluteURI + '/error.log');");
  $.writeln("  logFile.open('a');");
  $.writeln("  logFile.write(JSON.stringify(errorObject) + '\\n');");
  $.writeln("  logFile.close();");
  $.writeln("}");
  
  return { errorHandling: "global-handler-with-logging", recovery: "graceful" };
}

// Usage
catchSilentFailures();
```

---

## Performance Regression Diagnosis

### Identify What Slowed Down

```javascript
function diagnosePerformanceRegression() {
  /**
   * Find what caused plugin to become slower
   */
  
  $.writeln("=== PERFORMANCE REGRESSION DIAGNOSIS ===\n");
  
  $.writeln("Symptoms:");
  $.writeln("- Plugin was fast, now it's slow");
  $.writeln("- Specific operation got slower (e.g., import)");
  $.writeln("- No code changes in plugin itself");
  $.writeln("");
  
  $.writeln("Common Causes:");
  $.writeln("1. Dependency Update");
  $.writeln("   - Updated library (new version has bug)");
  $.writeln("   - Premiere update (compatibility issue)");
  $.writeln("   → Solution: Compare versions, revert & test");
  $.writeln("");
  $.writeln("2. Increased Data Volume");
  $.writeln("   - Processing larger files");
  $.writeln("   - More clips in project");
  $.writeln("   - Algorithm O(n) now O(n²)");
  $.writeln("   → Solution: Optimize algorithm, add caching");
  $.writeln("");
  $.writeln("3. Memory Pressure");
  $.writeln("   - System RAM full (lots of other apps)");
  $.writeln("   - Cache disabled or cleaned");
  $.writeln("   → Solution: Add more RAM, optimize memory");
  $.writeln("");
  $.writeln("Diagnosis Steps:");
  $.writeln("1. Baseline measurement (before regression):");
  $.writeln("   - Time operation: console.time('op')");
  $.writeln("   - Repeat N times, average");
  $.writeln("   - Record: v1.0.0 = 450ms");
  $.writeln("");
  $.writeln("2. Current measurement:");
  $.writeln("   - Same operation, same data");
  $.writeln("   - Record: v2.0.0 = 1200ms");
  $.writeln("   - Regression: 2.6x slower");
  $.writeln("");
  $.writeln("3. Bisect changes (binary search):");
  $.writeln("   - Revert to v1.5.0 → fast? slow?");
  $.writeln("   - Revert to v1.2.0 → fast? slow?");
  $.writeln("   - Find exact version where slowdown started");
  $.writeln("");
  $.writeln("4. Profile hot paths:");
  $.writeln("   - Measure time of each function");
  $.writeln("   - Find function that changed most");
  $.writeln("   - Compare code diff between versions");
  $.writeln("");
  $.writeln("5. Fix approach:");
  $.writeln("   - Revert problematic change (if safe)");
  $.writeln("   - Or optimize the slow function");
  $.writeln("   - Verify baseline restored");
  
  return { method: "baseline-bisect-profile", success: true };
}

// Usage
diagnosePerformanceRegression();
```

---

## Complex Debugging Checklist

- ☐ Monitor memory usage over time (identify leaks)
- ☐ Add comprehensive error logging (catch silent failures)
- ☐ Reproduce intermittent issues with stress testing
- ☐ Profile performance (identify hot paths and bottlenecks)
- ☐ Check for circular references (common memory leak source)
- ☐ Verify file handles are properly closed
- ☐ Add state snapshots before risky operations
- ☐ Use timeouts for all blocking operations
- ☐ Test race conditions with random delays
- ☐ Baseline performance before/after changes
- ☐ Add detailed logging with timestamps
- ☐ Set up global error handler with logging
- ☐ Monitor system resources during issues (CPU, memory, I/O)
- ☐ Use debugger breakpoints at suspected failure points
- ☐ Document findings in incident reports for future ref

---

## See Also

- Knowledge/debugging.md — Debugging fundamentals
- Knowledge/performance-profiling-guide.md — Performance analysis
- Knowledge/best-practices.md — Code quality standards
- Knowledge/faq-troubleshooting-tree.md — Decision trees

---

## Sources

- JavaScript Debugging: https://developer.chrome.com/docs/devtools/
- Memory Leak Detection: https://nodejs.org/en/docs/guides/simple-profiling/
- Performance Profiling: https://developer.mozilla.org/en-US/docs/Tools/Performance
- Adobe ExtendScript Debugging: https://github.com/ExtendScript/wiki
