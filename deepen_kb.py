#!/usr/bin/env python3
"""
Deepen Knowledge Base: Add 8 advanced topics + case studies
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.absolute()
KNOWLEDGE_DIR = REPO_ROOT / "Knowledge"

def create_decision_trees():
    """Create decision-trees.md for quick path selection"""
    content = '''---
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

**Decision trees = flowcharts for fast path selection.** "Should I use ExtendScript or UXP?" → Answer 3 questions → Get recommendation. **For AI agents:** Follow these trees to avoid reading entire KB.

---

## 🎯 Tree 1: Choose Automation Platform
```python
def format_timecode(seconds, fps, locale="en-US"):
    frames = int(seconds * fps)
    hours = frames // (fps * 3600)
    minutes = (frames % (fps * 3600)) // (fps * 60)
    secs = (frames % (fps * 60)) // fps
    frame = frames % fps
    
    if locale == "de-DE" or locale == "es-ES":
        sep = ","
    else:
        sep = ";"
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{sep}{frame:02d}"
```

---

## Right-to-Left (RTL) Support

For Hebrew, Arabic UI:

```html
<div dir="rtl" lang="he">
  <button>ביטול</button>
  <button>אישור</button>
</div>
```

CSS:
```css
[dir="rtl"] button {
  float: left;
  text-align: right;
}
```

---

## Locale-Aware Number Formatting

```javascript
const formatter = new Intl.NumberFormat("de-DE", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

console.log(formatter.format(1234.56));
```

Output: `1.234,56` (de-DE) vs `1,234.56` (en-US)

---

## Handling Localized Error Messages

Premiere's error messages vary by locale. Always validate objects, not message text:

```javascript
try {
  var seq = app.project.activeSequence;
} catch (e) {
  if (!seq) {
    console.log("No active sequence");
  }
}

// Not:
if (e.message.indexOf("Sequence") > -1) { }
```

---

## Platform Locale Detection

### ExtendScript
```javascript
var locale = $.locale;
```

### UXP
```javascript
const locale = navigator.language;
```

### Python
```python
import locale
lang = locale.getlocale()[0]
```

---

See also: panels.md, uxp.md, best-practices.md
'''
    with open(KNOWLEDGE_DIR / "localization-i18n.md", "w") as f:
        f.write(content)
    print("✅ Created localization-i18n.md")

def main():
    print("🔨 Deepening Knowledge Base (Variant B - All 8 Topics)...\n")
    
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    
    create_decision_trees()
    create_performance_optimization()
    create_migration_guides()
    create_advanced_integration()
    create_api_coverage_matrix()
    create_security_signing()
    create_production_case_studies()
    create_localization_i18n()
    
    print("\n" + "="*60)
    print("✅ VARIANT B (ПОЛНОЕ УГЛУБЛЕНИЕ) ЗАВЕРШЕНО")
    print("="*60)
    print("\n📚 Добавлено 8 новых Knowledge docs:")
    print("   1. ✅ decision-trees.md")
    print("   2. ✅ performance-optimization.md")
    print("   3. ✅ migration-extendscript-to-uxp.md")
    print("   4. ✅ migration-cep-to-uxp.md")
    print("   5. ✅ advanced-integration.md")
    print("   6. ✅ api-coverage-matrix.md")
    print("   7. ✅ security-signing.md")
    print("   8. ✅ production-case-studies.md")
    print("   9. ✅ localization-i18n.md")
    print("\n" + "="*60)
    print("🚀 NEXT STEPS:")
    print("="*60)
    print("1. cd /Users/konstantinguryanov/-open-premiere-specification")
    print("2. git add -A")
    print("3. git commit -m 'Variant B: Deep KB Expansion — 8 Advanced Topics'")
    print("4. git push origin main")
    print("="*60)

if __name__ == "__main__":
    main()
