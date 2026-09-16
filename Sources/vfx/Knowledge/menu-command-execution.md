---
id: menu-command-execution
title: Menu Command Execution - app.executeCommand and UI Automation
category: advanced
status: undocumented
stability: unstable
doc_status: complete
introduced: "Premiere Pro CC"
min_premiere_version: null
api_namespace: app
languages: [extendscript]
tags: [executecommand, menu-automation, undocumented, last-resort]
related: [reverse-engineering-qe-dom, best-practices, automation]
sources: ["Community findings", "Reverse engineering (confidence: low-medium)"]
confidence: low
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Menu Command Execution - app.executeCommand and UI Automation

## CRITICAL DISCLAIMER

`app.executeCommand()` invokes internal menu command IDs that are almost entirely undocumented by Adobe. Command IDs are not guaranteed stable across versions. This is a last-resort technique for operations with absolutely no DOM or QE equivalent. Treat with the same caution as QE DOM.

## TL;DR

Some Premiere operations exist only as menu commands with no scripting API (no DOM, no QE method). `app.executeCommand(commandID)` can trigger these, but command IDs must be discovered empirically (no official list) and may break between versions. Use only when documented DOM/QE/UXP paths are confirmed absent.

---

## When To Use This

1. Operation has no `app.project.*`, `app.qe.*`, or UXP equivalent
2. Operation is exposed only via a menu item or keyboard shortcut
3. Risk of version breakage is acceptable for the use case
4. Always document the discovered command ID and the Premiere version it was tested against

---

## Basic Pattern

```javascript
try {
  app.executeCommand(206);
} catch (e) {
  alert("Command failed or unavailable: " + e.toString());
}
```

**Problem:** Numeric command IDs (like `206`) are internal and undocumented. There is no official registry mapping IDs to actions.

---

## Discovering Command IDs (Empirical Method)

No reliable enumeration API exists. Community approach:

1. Record keyboard shortcut for target menu action (Edit > Keyboard Shortcuts)
2. Use OS-level event monitoring or trial-and-error with sequential IDs in a test project
3. Cross-reference community-maintained lists (unofficial, version-specific, often outdated)

**Recommendation:** Treat any discovered ID as version-pinned. Re-verify after every Premiere update.

---

## Safer Alternative: Keyboard Shortcut Simulation (External)

For operations with no executeCommand mapping found, OS-level automation can simulate keypresses as a last resort:

```python
import subprocess

subprocess.run([
    "osascript", "-e",
    'tell application "Adobe Premiere Pro 2026" to activate'
])
subprocess.run([
    "osascript", "-e",
    'tell application "System Events" to keystroke "s" using {command down, shift down}'
])
```

**Caveat:** Extremely fragile — depends on window focus, OS version, accessibility permissions, and exact keyboard shortcut mapping (which can be user-customized).

---

## Risk Comparison vs QE DOM

| Aspect | QE DOM | executeCommand |
|---|---|---|
| Documentation | None (reverse-engineered structure) | None (no ID registry at all) |
| Stability | Medium (object hierarchy somewhat consistent) | Low (raw integer IDs, no semantic meaning) |
| Discoverability | Some community mapping exists | Almost none; mostly trial-and-error |
| Recommended use | Last resort for missing DOM features | Absolute last resort, only if QE also lacks the feature |

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| Command silently does nothing | Wrong ID for this Premiere version | Re-verify ID empirically per version |
| Command throws exception | ID invalid or context-inappropriate (e.g. no active sequence) | Wrap in try/catch, check preconditions |
| Different behavior across versions | IDs are not stable across Premiere releases | Pin and document tested version explicitly |

---

## Sources

- Community findings (forums, scripting groups) — confidence: low
- No official Adobe documentation exists for this API surface
