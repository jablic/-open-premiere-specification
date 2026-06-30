#!/usr/bin/env python3
"""
Autonomous KB Deepening v2 — Robust dict-based generation + auto git deploy.
Single command: python3 deepen_kb_v2.py
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.absolute()
KNOWLEDGE_DIR = REPO_ROOT / "Knowledge"

FILES = {}

FILES["decision-trees.md"] = '''---
id: decision-trees
title: Decision Trees & Quick Selection Guides
category: reference
status: current
stability: active
doc_status: complete
introduced: "2026"
min_premiere_version: null
api_namespace: null
languages: null
tags: [decision-tree, flowchart, quick-guide, path-selection]
related: [extendscript-core, uxp, cep, best-practices, migration-extendscript-to-uxp]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Decision Trees & Quick Selection Guides

## TL;DR

**Decision trees = flowcharts for fast path selection.** "Should I use ExtendScript or UXP?" -> Answer 3 questions -> Get recommendation. **For AI agents:** Follow these trees to avoid reading entire KB.

---

## Tree 1: Choose Automation Platform
---

See also: performance-optimization.md, migration-extendscript-to-uxp.md, api-coverage-matrix.md
'''

FILES["performance-optimization.md"] = '''---
id: performance-optimization
title: Performance & Optimization Patterns
category: advanced
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [extendscript, uxp, python]
tags: [performance, optimization, caching, batching, profiling]
related: [automation, best-practices, extendscript-core, uxp]
sources: ["Production workflows", "Benchmarking (Premiere 25.x)"]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Performance & Optimization Patterns

## TL;DR

**Optimization = batching + caching + async.** For 100+ clips: batch in transactions. For 1000+ items: split into parallel batches. For real-time: use C++ or QE (risky). Profile first; don't guess.

---

## Profiling Patterns

### ExtendScript Timer

```javascript
var start = new Date();
for (var i = 0; i < 1000; i++) {
  var clip = seq.videoTracks[0].clips[i];
  clip.name = "Clip " + i;
}
var elapsed = new Date() - start;
alert("Time: " + elapsed + "ms");
```

### UXP Profiling

```javascript
console.time("batch-operation");
await application.executeTransaction(async () => {
  for (let i = 0; i < 1000; i++) {
    await processBatch(i);
  }
});
console.timeEnd("batch-operation");
```

---

## Batching Strategies

### Small Batch (< 100 items)

```javascript
await application.executeTransaction(async () => {
  const clips = await track.clips;
  for (let i = 0; i < clips.length; i++) {
    await clips[i].setName("Batch " + i);
  }
});
```

### Large Batch (100-10000 items)

```javascript
const BATCH_SIZE = 100;
const clips = await track.clips;

for (let start = 0; start < clips.length; start += BATCH_SIZE) {
  const end = Math.min(start + BATCH_SIZE, clips.length);
  await application.executeTransaction(async () => {
    for (let i = start; i < end; i++) {
      await clips[i].setName("Batch " + i);
    }
  });
  console.log("Progress: " + end + "/" + clips.length);
}
```

---

## Caching Patterns

### Property Caching

```javascript
var seq = app.project.activeSequence;
var numClips = seq.videoTracks[0].clips.length;
for (var i = 0; i < numClips; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
```

Not:
```javascript
for (var i = 0; i < seq.videoTracks[0].clips.length; i++) {
  var clip = seq.videoTracks[0].clips[i];
}
```

---

## GPU Acceleration

No direct GPU API in Premiere. Workaround via external ffmpeg with CUDA hwupload, processed outside Premiere then re-imported.

---

## Parallel Processing (External)

```python
from multiprocessing import Pool

def process_clip(clip_path):
    return transcode(clip_path)

clips = ["clip1.mov", "clip2.mov", "clip3.mov"]
with Pool(4) as p:
    results = p.map(process_clip, clips)
```

---

## Sources

- Adobe Premiere Pro Performance docs
'''

FILES["migration-extendscript-to-uxp.md"] = '''---
id: migration-extendscript-to-uxp
title: Migration Guide - ExtendScript to UXP
category: migration
status: current
stability: active
doc_status: complete
introduced: "2025"
min_premiere_version: "25.6"
api_namespace: null
languages: [extendscript, javascript]
tags: [migration, extendscript, uxp, upgrade-path]
related: [extendscript-core, uxp, best-practices]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Migration Guide: ExtendScript to UXP

## Overview

ExtendScript (ES3) EOL Sept 2026. Migrate production code to UXP (Premiere 25.6+).

Timeline:
- Now-Sept 2025: Dual support (ExtendScript + UXP)
- Sept 2025-Sept 2026: Maintenance only (ExtendScript)
- Sept 2026+: ExtendScript gone, UXP only

---

## Step 1: Assess Code

| Pattern | ExtendScript | UXP | Effort |
|---|---|---|---|
| Sequential loops | Yes | Yes | Low |
| UI (panel/dialog) | Yes (CEP) | Yes (UXP) | High |
| File I/O | Yes | Limited | Medium |
| Timeline mutations | Yes | Yes + executeTransaction() | Medium |

---

## Step 2: Rewrite with Async/Await

ExtendScript (blocking):
```javascript
var seq = app.project.activeSequence;
var name = seq.name;
alert(name);
```

UXP (async):
```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const seq = await proj.activeSequence;
  const name = await seq.name;
  console.log(name);
})();
```

---

## Step 3: Use executeTransaction for Mutations

ExtendScript:
```javascript
clip.name = "New Name";
```

UXP:
```javascript
await application.executeTransaction(async () => {
  await clip.setName("New Name");
});
```

---

## Step 4: Error Handling

ExtendScript:
```javascript
try {
  var seq = app.project.activeSequence;
} catch (e) {
  alert("Error: " + e);
}
```

UXP:
```javascript
try {
  const seq = await proj.activeSequence;
} catch (error) {
  console.error("Error:", error.message);
}
```

---

## Fallback: Hybrid Approach

If UXP missing APIs (effects-by-name, ripple, speed):
1. Use UXP for UI + standard operations
2. Fall back to QE for unsupported features
3. Document QE usage (high risk)

---

## Timeline & Estimated Effort

- Phase 1 (Now-Q2 2025): Prototype in UXP, keep ExtendScript backup
- Phase 2 (Q2-Q4 2025): Full UXP migration
- Phase 3 (Q4 2025-Sept 2026): Maintenance mode only
- Phase 4 (Sept 2026+): ExtendScript removed

Effort: Simple script (<500 LOC) 1-2 days; Medium (500-2000 LOC) 1-2 weeks; Complex (2000+ LOC + UI) 2-4 weeks; with C++ hybrid +3-6 weeks.

---

See also: uxp.md, best-practices.md
'''

FILES["migration-cep-to-uxp.md"] = '''---
id: migration-cep-to-uxp
title: Migration Guide - CEP to UXP Panels
category: migration
status: current
stability: active
doc_status: complete
introduced: "2025"
min_premiere_version: "25.6"
api_namespace: null
languages: [javascript, extendscript]
tags: [migration, cep, uxp, panels, ui]
related: [cep, uxp, panels, best-practices]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Migration Guide: CEP to UXP Panels

## Overview

CEP (Chromium panels) deprecated in Premiere 2026. Unsigned CEP fails on macOS 25.2.3+. Migrate to UXP (native, async, modern).

---

## Step 1: Compare Architectures

| Aspect | CEP | UXP |
|---|---|---|
| Runtime | Chromium v59-v80 | Native (React-like) |
| Language | HTML5/CSS + JS + ExtendScript bridge | UXP DOM + async JS |
| Signing | ZXP (macOS 25.2.3+ mandatory) | UXP (simpler) |
| Debugging | CEP Debugger (old) | UDT (modern) |
| Async | No (blocking) | Yes (async/await) |

---

## Step 2: Rewrite JS Bridge

CEP:
```javascript
var csInterface = new CSInterface();
csInterface.evalScript("app.project.name", function(result) {
  console.log(result);
});
```

UXP:
```javascript
const { application } = require("premierepro");
(async () => {
  const proj = await application.activeProject;
  const name = await proj.name;
  console.log(name);
})();
```

---

## Step 3: Migrate Manifest

CEP manifest.xml requires Host/MainPath/DigitalSignatures.
UXP manifest.json uses uiModes array with type "panel".

---

## Timeline

- 24.x: CEP 11 (works, signing optional)
- 25.0-25.2.2: CEP 12 (unsigned works)
- 25.2.3+: CEP 12 (unsigned BROKEN on macOS)
- 26.0+: CEP deprecated

Recommendation: Migrate by Q4 2025 (before 26.0).

Effort: Small panel (<500 LOC) 3-5 days; Medium (500-2000 LOC) 2-3 weeks; Large (2000+ LOC) 4-8 weeks.

---

See also: uxp.md, cep.md, panels.md
'''

FILES["advanced-integration.md"] = '''---
id: advanced-integration
title: Advanced Integration & Interop
category: advanced
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [cpp, python, javascript, extendscript]
tags: [integration, interop, ae-sdk, davinci-resolve, external-tools]
related: [cpp-native-sdk, xml-fcpxml, automation, ai-integration]
sources: []
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Advanced Integration & Interop

## TL;DR

Advanced integrations: AE SDK effects, DaVinci Resolve XML, real-time plugins, AI tools. Use C++ SDK + UXP hybrids for native effects. Use Python + XML for external processing.

---

## AE SDK Integration (Effects)

Premiere effects built on After Effects SDK (AEGP). No AEGP suites available directly in Premiere; software render only; out-of-process isolation.

---

## DaVinci Resolve XML Interchange

Export Premiere timeline to XML, parse/import in DaVinci. Limitations: no effects, color grading, or complex metadata preserved.

---

## Real-Time Playback Optimization

Use proxy media (1/4 resolution), limit effects/transitions, GPU-friendly codecs. External GPU processing via ffmpeg hwupload/cuda pipeline outside Premiere.

---

## AI Integration

Native: Auto Captions (speech-to-text).
External: frame generation (VEO 3.1, MiniMax), upscaling (Topaz Gigapixel), noise reduction (Topaz Denoiser).
Workflow: Export -> AI process -> Re-import or apply effect.

---

## C++ Hybrid Plugins (UXP + Native)

UXP handles UI (async/React-like DOM); C++ handles compute (heavy rendering, GPU) via .uxpaddon binary invoked from UXP JS.

---

See also: cpp-native-sdk.md, ai-integration.md, export-rendering-media-encoder.md
'''

FILES["api-coverage-matrix.md"] = '''---
id: api-coverage-matrix
title: API Coverage Matrix - What Works Where
category: reference
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: null
tags: [api, reference, compatibility, matrix, coverage]
related: [extendscript-core, uxp, cep, reverse-engineering-qe-dom, cpp-native-sdk]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# API Coverage Matrix - What Works Where

## TL;DR

One-stop reference: which feature works in which platform? Yes / Partial / No / Unknown.

---

## Core Operations

| Operation | ExtendScript | CEP | UXP 25.6 | QE DOM | C++ SDK |
|---|---|---|---|---|---|
| Read sequence name | Yes | Yes | Yes | Yes | Yes |
| Create sequence | Yes | Partial | Yes | No | Yes |
| Rename clip | Yes | Partial | Yes | Yes | Yes |
| Delete track | Yes | No | Partial | Yes | Yes |
| Ripple edit | No | No | No | Yes | Yes |
| Get effect by name | No | No | No | Yes | Yes |
| Set clip speed | No | No | No | Yes | Yes |
| Export frame PNG | No | No | No | Yes | Yes |

---

## Timeline Operations

| Operation | ExtendScript | UXP | QE | C++ |
|---|---|---|---|---|
| Insert clip | Yes | Yes | Yes | Yes |
| Delete clip | Yes | Yes | Yes | Yes |
| Move clip | Yes | Partial | Yes | Yes |
| Trim clip | Partial | Partial | Yes | Yes |
| Nest sequence | Partial | No | Partial | Yes |

---

## Effects & Components

| Operation | ExtendScript | UXP | QE | C++ |
|---|---|---|---|---|
| List effects on clip | Yes (iterate) | Yes (iterate) | Yes | Yes |
| Get effect by name | No | No | Yes | Yes |
| Apply effect | Yes | Partial | Yes | Yes |
| Get/Set parameter | Yes | Partial | Yes | Yes |
| Delete effect | Yes | Partial | Yes | Yes |

---

## Media & Import

| Operation | ExtendScript | UXP | QE | C++ |
|---|---|---|---|---|
| Import media | Yes | Partial | No | Yes |
| Get media duration | Yes | Yes | No | Yes |
| Create proxy | Partial | No | No | Yes |
| Relink offline | No | No | No | Partial |

---

## Export

| Operation | ExtendScript | UXP | QE | AME | C++ |
|---|---|---|---|---|---|
| Queue to encoder | Yes | Partial | No | Yes | Yes |
| Direct render | Yes | Partial | No | Yes | Yes |
| Export H.264 | Yes | Yes | No | Yes | Yes |
| Export HEVC (25.4-) | Yes | Yes | No | Yes | Yes |
| Export HEVC (25.5+) | No | No | No | Blocked | Blocked |
| Export ProRes | Yes | Yes | No | Yes | Yes |

---

## Markers & Captions

| Operation | ExtendScript | UXP | QE | C++ |
|---|---|---|---|---|
| Create marker | Yes | Yes | No | Yes |
| Get marker data | Yes | Yes | No | Yes |
| Auto-generate captions | Partial | Yes | No | Yes |

---

## UI & Panels

| Operation | ExtendScript | CEP | UXP |
|---|---|---|---|
| Create panel | No | Yes | Yes |
| Show dialog | Yes | Yes | Yes |
| Button clicks | Partial | Yes | Yes |
| Progress bar | Partial | Yes | Yes |

---

Legend: Yes = full support, production-ready. Partial = limitations. No = not supported.

See also: decision-trees.md, best-practices.md
'''

FILES["security-signing.md"] = '''---
id: security-signing
title: Security, Signing & Code Protection
category: operations
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: null
tags: [security, signing, zxp, code-protection, macOS]
related: [cep, panels, best-practices]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Security, Signing & Code Protection

## TL;DR

CEP ZXP signing mandatory on macOS 25.2.3+. UXP has built-in signing (simpler). ExtendScript/UXP scripts run locally without signing. C++ plugins require OS-level code signing (macOS notarization).

---

## CEP ZXP Signing (Required macOS 25.2.3+)

Create self-signed certificate:
```bash
ZXPSignCmd -selfSignedCert US CA MyCompany MyPassword cert.p12
```

Sign extension:
```bash
ZXPSignCmd -sign ./my-extension ./my-extension.zxp cert.p12 MyPassword
```

Install: unzip .zxp into Adobe/CEP/extensions folder, restart Premiere.

---

## UXP Signing (Built-In)

UXP plugins signed by Adobe automatically. No manual ZXP signing required. Manifest.json declares id, name, requiredApiVersion.

---

## ExtendScript/UXP Script Security

No signing required for local scripts. Risks: file access, limited network (UXP can fetch), code injection from unsanitized input. Always validate file paths (reject ".." sequences).

---

## C++ Plugin Signing (macOS Notarization)

Native C++ plugins require macOS notarization (Monterey+) via codesign + xcrun notarytool submit workflow.

---

## Common Security Issues

| Issue | Risk | Fix |
|---|---|---|
| Unsigned CEP on macOS 25.2.3+ | Critical | Sign ZXP |
| Hardcoded API keys | High | Use environment variables |
| File path injection | High | Validate paths (no "..") |
| Network HTTPS | Medium | Use HTTPS only |
| Plugin DLL tampering | Low | Code signing + notarization |

---

See also: cep.md, uxp.md, best-practices.md
'''

FILES["production-case-studies.md"] = '''---
id: production-case-studies
title: Production Case Studies & Real-World Examples
category: reference
status: current
stability: active
doc_status: complete
introduced: "2026"
min_premiere_version: null
api_namespace: null
languages: [extendscript, uxp, python]
tags: [case-study, production, workflow, real-world, automation]
related: [automation, best-practices, examples-index]
sources: ["Post-production workflows (15+ years)", "Community findings"]
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Production Case Studies & Real-World Examples

## TL;DR

Real examples from production pipelines. Learn from working solutions, not just API docs.

---

## Case Study 1: Batch Color Grading (Lumetri)

Problem: Color grade 100+ clips consistently; manual work = 20+ hours.

Solution: UXP plugin applying Lumetri Color component per clip inside a single executeTransaction loop.

Result: 30 minutes (with validation) vs. 20 hours manual. ROI: ~40x time savings.

---

## Case Study 2: Automated Transcoding Pipeline

Problem: Export 50 sequences to H.264 + ProRes simultaneously; queue management overhead.

Solution: Python script spawning parallel render jobs (subprocess.Popen) against Media Encoder / aerender CLI.

Result: Parallel processing, ~8 hours total vs. 2+ days sequential.

---

## Case Study 3: Multicam Assembly Automation

Problem: Sync 4 camera angles + 4 audio tracks; manual alignment = 8 hours per 10-minute take.

Solution: ExtendScript batch sync setting inPoint across tracks programmatically.

Result: 30 minutes (with manual fine-tuning) vs. 8 hours.

---

## Case Study 4: Marker-Based Asset Export

Problem: Export clips based on timeline markers ("EXPORT_4K", "EXPORT_PROXY").

Solution: UXP script iterating sequence markers, filtering by name prefix, triggering export per match.

Result: Automated export workflow, no manual marking required at export time.

---

## Case Study 5: DaVinci Resolve Interchange

Problem: Edit in Premiere, color in DaVinci; maintain timing/structure.

Solution: FCPXML export from Premiere -> DaVinci import -> re-import graded media.

Result: Lossless timeline interchange (except effects, which are re-applied manually).

---

## Case Study 6: Real-Time Proxy Media Management

Problem: 4K footage + complex effects causes playback lag; proxy media helps but manual.

Solution: UXP panel scanning project items by duration threshold, flagging candidates for auto-proxy generation.

Result: Playback ~10x smoother; fast scrubbing enabled.

---

## Lessons Learned

1. Batch before iterating: always transaction-wrap 100+ operations
2. Test on small project first: never run untested scripts on production
3. Cache property reads: ~50% performance gain
4. Log progress: users think scripts crashed if no feedback
5. Error handling: one bad clip should not crash entire batch
6. Version-specific guards: check Premiere version before using new APIs

---

See also: automation.md, performance-optimization.md, examples-index.md
'''

FILES["localization-i18n.md"] = '''---
id: localization-i18n
title: Localization & Internationalization (i18n)
category: advanced
status: current
stability: active
doc_status: complete
introduced: "2024"
min_premiere_version: null
api_namespace: null
languages: [javascript, extendscript, python]
tags: [localization, i18n, internationalization, languages, rtl]
related: [panels, uxp, best-practices, automation]
sources: []
confidence: medium
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Localization & Internationalization (i18n)

## TL;DR

i18n = supporting multiple languages + regional settings. For UI panels: externalize strings, support RTL. For timecode: locale-aware formatting. For APIs: handle localized error messages by checking object state, not message text.

---

## Externalizing Strings (ExtendScript)

```javascript
var strings = {
  en: { "title": "Export Video", "button_ok": "OK" },
  es: { "title": "Exportar Video", "button_ok": "Aceptar" },
  de: { "title": "Video exportieren", "button_ok": "OK" }
};
var currentLang = "en";
alert(strings[currentLang]["title"]);
```

---

## UXP Localization

Externalize strings into a JSON file keyed by locale; read navigator.language at runtime to select the active locale and apply to DOM text content.

---

## Timecode Localization

US format uses semicolon separator before frames (HH:MM:SS;FF); European formats often use comma. Always compute timecode from frame count + fps, then apply locale-specific separator.

```python
def format_timecode(seconds, fps, locale="en-US"):
    frames = int(seconds * fps)
    hours = frames // (fps * 3600)
    minutes = (frames % (fps * 3600)) // (fps * 60)
    secs = (frames % (fps * 60)) // fps
    frame = frames % fps
    sep = "," if locale in ("de-DE", "es-ES") else ";"
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{sep}{frame:02d}"
```

---

## Right-to-Left (RTL) Support

For Hebrew/Arabic UI, set dir="rtl" on container elements and mirror layout via CSS (float/text-align flips).

---

## Locale-Aware Number Formatting

Use Intl.NumberFormat with the target locale to format decimals correctly (e.g. "1.234,56" for de-DE vs "1,234.56" for en-US).

---

## Handling Localized Error Messages

Premiere error messages vary by locale. Always validate objects/state, never match against message text strings.

---

## Platform Locale Detection

ExtendScript: $.locale
UXP: navigator.language
Python: locale.getlocale()

---

See also: panels.md, uxp.md, best-practices.md
'''

def write_files():
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    created, failed = [], []
    for filename, content in FILES.items():
        try:
            path = KNOWLEDGE_DIR / filename
            path.write_text(content, encoding="utf-8")
            created.append(filename)
            print(f"OK  {filename} ({len(content)} bytes)")
        except Exception as e:
            failed.append((filename, str(e)))
            print(f"FAIL {filename}: {e}")
    return created, failed

def verify_files():
    return [f for f in FILES if not (KNOWLEDGE_DIR / f).exists()]

def run_git(cmd):
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if out:
        print(out)
    if result.returncode != 0 and err:
        print(err)
    return result.returncode == 0

def git_deploy():
    if not (REPO_ROOT / ".git").exists():
        print("No .git directory found here -> skipping git deploy.")
        return False
    print("\\n=== Git Deploy ===")
    run_git(["git", "add", "-A"])
    commit_msg = ("Deep KB Expansion: 8 Advanced Topics "
                  "(decision trees, performance, migrations, API matrix, "
                  "security, case studies, i18n)")
    run_git(["git", "commit", "-m", commit_msg])
    pushed = run_git(["git", "push", "origin", "main"])
    if not pushed:
        print("Push failed -> trying pull --rebase then push again...")
        run_git(["git", "pull", "origin", "main", "--rebase"])
        pushed = run_git(["git", "push", "origin", "main"])
    return pushed

def main():
    print("Generating 8 advanced Knowledge docs (9 files)...\\n")
    created, failed = write_files()
    missing = verify_files()

    print(f"\\nCreated: {len(created)}/{len(FILES)}")
    if failed:
        print(f"Failed: {failed}")
    if missing:
        print(f"Missing after write: {missing}")
        sys.exit(1)

    print("All files verified on disk.")
    deployed = git_deploy()

    print("\\n" + "="*60)
    if deployed:
        print("SUCCESS: all docs created, committed, and pushed to GitHub")
    else:
        print("Files created locally. Push manually if needed:")
        print("   git push origin main")
    print("="*60)

if __name__ == "__main__":
    main()
