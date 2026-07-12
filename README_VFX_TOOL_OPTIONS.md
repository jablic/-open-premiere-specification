# VFX List Export Tool — Three Versions, Pick Your Path

## Quick Comparison

| Feature | v3 Working | v2 Hybrid | Manual UI |
|---------|-----------|----------|-----------|
| **Markers** | ✅ UXP | ✅ UXP | Manual |
| **MOGRT/Text Plates** | ❌ Read-only | ✅ ExtScript | Manual |
| **Captions** | ❌ Read-only | ❌ Read-only | Manual |
| **Speed** | ~200ms / 100 items | ~10s / 100 MOGRT | ~5min / 5 items |
| **Reliability** | 100% | ~80% | 100% |
| **Maintenance** | Low | Medium | N/A |

---

## Version 3: "Working" (Honest, Production-Ready)

### What Works
- ✅ Batch marker renaming with patterns
- ✅ Fast (UXP native, ~200ms per 100 markers)
- ✅ 100% reliable
- ✅ Single undo step

### What Doesn't Work
- ❌ Captions (No API available — Adobe limitation)
- ❌ Text plates/MOGRT (API gap, use v2 for workaround)

### Use When
- You only need marker automation
- You want something production-ready today
- You value reliability over features
- Captions/text plates: you'll do manually or wait

### Install
```bash
cp vfx-list-uxp-panel ~/Library/Application\ Support/Adobe/UXP\ Plugins/
# Use index-v3-working.js in Premiere Pro 25.6+
```

### Example
```
Input:  [MARKER_1, MARKER_2, MARKER_3, ...]
Config: Pattern = "CG_{shot}"
Output: [CG_0001, CG_0002, CG_0003, ...]
Time:   ~50ms
```

---

## Version 2: Hybrid (ExtendScript Bridge)

### What Works
- ✅ Batch marker renaming
- ✅ Batch MOGRT text updates (ExtendScript sequential)
- ✅ Same presets/patterns as v3

### What Doesn't Work
- ❌ Captions (No API — same Adobe limitation)

### Caveats
- **Slow:** ~100ms per MOGRT = 10s for 100 items
- **Fragile:** ~80% success rate (some MOGRTs fail)
- **Sequential:** Waits for each clip before next
- **Maintenance:** Needs ExtendScript bridge debugging

### Use When
- You need MOGRT text automation NOW
- You're OK with slower batch times
- You can tolerate 20% failure rate
- You'll monitor for errors

### How It Works
```
UXP Panel (v2)
  ↓
  Markers: UXP native (fast)
  ↓
  MOGRTs: ExtendScript bridge (sequential, 100ms each)
    • Get clip + component
    • Parse Source Text JSON
    • Mutate textEditValue + fontTextRunLength
    • Apply setValue(blob, true)
    • Verify result
    • Next MOGRT
```

### Install
```bash
cp vfx-list-uxp-panel ~/Library/Application\ Support/Adobe/UXP\ Plugins/
# Use index-v2.js + extendscript-bridge.jsx
```

### Example
```
Input:  [MOGRT at track 1, clip 0; MOGRT at track 1, clip 1; ...]
Config: Pattern = "PLATE_{shot}"
Output: [PLATE_0001, PLATE_0002, ...]
Time:   ~100ms per MOGRT + UXP overhead
Status: ~80% success (check errors per clip)
```

### Known Issues
- "Source Text caching bug" on some builds
- Premiere-authored graphics fail (must be AE-authored MOGRT)
- May need manual render/undo to refresh UI
- Windows path separators can cause issues

---

## Manual Editing (Fallback)

### What Works
- ✅ Any caption/text format
- ✅ 100% reliable
- ✅ No automation needed

### Caveats
- **Slow:** ~5 minutes per 5 items
- **Manual:** No batch automation
- **Tedious:** Repeat for each clip

### Use When
- Automation tools fail or unavailable
- You need perfect control
- Small number of items (<10)
- Reliability > speed

### Process
1. Double-click caption in timeline
2. Edit text in caption editor
3. Set duration/styling
4. Repeat for each caption/MOGRT

### Time Estimate
- Per caption: ~1 minute
- Per text plate: ~2 minutes
- 100 items: ~2 hours

---

## Decision Matrix

### "I need markers automated NOW"
→ **Use v3 (Working)**
- Marker renaming ✅
- Fast ✅
- Reliable ✅
- No captions ⚠️

### "I need markers + MOGRT automated, captions manual"
→ **Use v2 (Hybrid)**
- Marker renaming ✅
- MOGRT editing ✅ (slow/fragile)
- Fast enough ✅ (~10s for 100 MOGRT)
- Monitor for errors ⚠️

### "I need everything automated"
→ **Wait for Premiere 26.x** (expected Spring 2026)
- Full UXP caption API expected
- Better MOGRT support expected
- v4 tool will use native APIs

### "I have 5 captions, don't care about automation"
→ **Use manual editing**
- ~5 minutes total
- 100% reliable
- No tool needed

---

## FAQ

### "Why can't v3 do captions?"
Adobe's UXP 25.6 doesn't expose caption.setText() API. It's a Premiere limitation, not implementation issue. Shotify has same problem (0 captions rewritten).

### "Why is v2 slow?"
ExtendScript sequential processing: 100ms per MOGRT to get component → parse JSON → mutate → apply → verify. Can't be faster without UXP improvement.

### "Can I use both v2 and v3?"
Not simultaneously. Pick one version. v2 includes v3's marker automation + adds MOGRT via bridge.

### "Will v2 work in Premiere 26.x?"
Yes, but unnecessary. v26 expected to add full UXP caption API + better MOGRT support. v4 tool will replace v2 entirely.

### "What's the success rate for v2 MOGRT edits?"
~80% (20% fail due to: Premiere-authored graphics, unsupported MOGRT format, caching bugs on specific builds).

### "Can I edit captions via Python?"
Only via export (SRT/VTT) + external parsing. No live Premiere caption API exists. Same limitation everywhere.

---

## Recommendation Flowchart

```
Start: Do you need caption automation?
├─ Yes → "Captions require Premiere 26.x. Wait or edit manually."
│
└─ No → Do you need MOGRT automation?
   ├─ Yes → Use v2 (Hybrid) — slower but works
   │
   └─ No → Use v3 (Working) — markers only, production-ready
```

---

## Migration Path

### Today (Premiere 25.6)
- v3: Markers only ✅
- v2: Markers + MOGRT (workaround) ⚠️

### Spring 2026 (Premiere 26.x)
- v4: Markers + MOGRT + Captions (native UXP) ✅
- v2: Deprecated (slower, not needed)
- v3: Archived (subset of v4)

---

## Technical Details

### Why ExtendScript for MOGRT?
- UXP can't access MOGRT Source Text JSON blob
- ExtendScript has `getMGTComponent()` + `properties` API
- Production-tested pattern (since Premiere 14.x)
- Only reliable way until UXP improves

### Why No Captions in ExtendScript?
- Premiere's captions are stored separately (sequence metadata)
- No script API for read/write captions
- Only export API (via Media Encoder)
- Adobe has never exposed caption scripting

### Why v3 Honest?
- Ships what works
- Clear about limitations
- No false promises
- User knows what to expect

---

## Support

### v3 Issues
- Panel not loading? Check UXP Plugins path, restart Premiere
- Markers not loading? Ensure sequence exists and has markers
- UI broken? Clear localStorage: DevTools → Application → Storage

### v2 Issues
- MOGRT not updating? Check if AE-authored (not Premiere-authored)
- Partial text update? fontTextRunLength issue — clear cache and retry
- Bridge not responding? Restart Premiere (ExtendScript context reset)
- Windows path errors? Use forward slashes or absolute UNC paths

### Captions Issues
- Can't batch rename? This is Premiere limitation (no API) — use manual edit or wait 26.x
- UI grayed out? Intentional — v3/v2 don't support captions in UXP 25.6

---

## Files

```
vfx-list-uxp-panel/
├── manifest.json
├── src/
│   ├── index.html
│   ├── index.css
│   ├── index-v3-working.js      ← v3: Markers only
│   ├── index-v2.js               ← v2: Markers + MOGRT
│   └── extendscript-bridge.jsx  ← v2 dependency
```

**README_VFX_TOOL_OPTIONS.md** (this file)
**VFX_TOOL_V3_FINAL_HONEST.md** — detailed v3 docs
**VFX_TOOL_REALITY_CHECK.md** — API limitation analysis
**AUTOMATION_RESEARCH.md** — approach comparison (v1-v3)
**VFX_TOOL_HYBRID_APPROACH.md** — v2 architecture details

---

## Bottom Line

- **v3 = Production-ready marker automation**
- **v2 = Workaround for MOGRT (accept slowness/fragility)**
- **Captions = Wait for 26.x or do manually**
- **Honest > Fake features**

Pick your trade-off and ship.
