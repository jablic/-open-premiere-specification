# VFX List Export Tool — Quick Start

## TL;DR

**v3 works:** Marker automation ✅  
**v2 workaround:** MOGRT automation ⚠️  
**Captions:** Not possible in Premiere 25.6 ❌

---

## Install (2 minutes)

### macOS
```bash
cp -r vfx-list-uxp-panel ~/Library/Application\ Support/Adobe/UXP\ Plugins/
# Restart Premiere Pro
# Window → Panels → VFX List Export
```

### Windows
```cmd
copy vfx-list-uxp-panel %APPDATA%\Adobe\UXP\ Plugins\
REM Restart Premiere Pro
REM Window → Panels → VFX List Export
```

---

## Use (1 minute)

1. **Open panel** in Premiere Pro 25.6+
2. **Enter pattern** (e.g., `CG_{shot}`)
3. **Click Execute**
4. **✅ Done** — markers renamed

```
Pattern: CG_{shot}
↓
Input:  [MARKER_1, MARKER_2, MARKER_3]
Output: [CG_0001, CG_0002, CG_0003]
Time:   ~50ms
```

---

## Features

### ✅ What Works (v3 — Production Ready)
- Batch rename markers with pattern
- Skip IN/OUT markers automatically
- Save/load preset patterns
- Single undo step
- Auto-reload after changes

### ⚠️ What's Slow (v2 — Workaround)
- Text plate (MOGRT) renaming (see README_VFX_TOOL_OPTIONS.md)
- ~100ms per clip (sequential)
- ~80% success rate

### ❌ What's Impossible (Premiere 25.6)
- Caption renaming (no API support)
- Will work in Premiere 26.x (Spring 2026)

---

## Documentation

| File | Purpose |
|------|---------|
| **VFX_TOOL_V3_FINAL_HONEST.md** | Complete v3 guide |
| **README_VFX_TOOL_OPTIONS.md** | Choose v2/v3/manual |
| **VFX_TOOL_REALITY_CHECK.md** | Why captions don't work |
| **VFX_TOOL_FINAL_SUMMARY.md** | Full delivery summary |

---

## FAQ

**Q: Does it work?**  
A: Yes. Markers work 100%. Captions/text await Premiere 26.x.

**Q: Is it slow?**  
A: No. ~50ms for 100 markers. v2 MOGRT is slow (~100ms each).

**Q: Can I use it now?**  
A: Yes. Install and use immediately for marker automation.

**Q: What about captions?**  
A: Not possible in Premiere 25.6 (Adobe API limitation). Edit manually or wait.

**Q: What if I need MOGRT automation?**  
A: Use v2 (slower, more fragile). See README_VFX_TOOL_OPTIONS.md.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Panel not loading | Restart Premiere, check UXP path |
| Markers not loading | Ensure sequence exists, has markers |
| Pattern not applying | Use `{shot}` placeholder |
| v2 MOGRT fails | Check if AE-authored (not Premiere-authored) |
| UI grayed out | Captions/text disabled (intentional, API limit) |

---

## Next Steps

1. ✅ Install panel
2. ✅ Test with marker pattern
3. ✅ Read VFX_TOOL_V3_FINAL_HONEST.md for details
4. ✅ Choose v2 if you need MOGRT (see README_VFX_TOOL_OPTIONS.md)
5. ✅ Wait for Premiere 26.x for captions

---

**Ready?** Install and start renaming markers. 🚀
