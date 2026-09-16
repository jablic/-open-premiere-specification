---
id: aaf-interchange
title: AAF (Advanced Authoring Format) Interchange
category: interop
status: current
stability: active
doc_status: complete
introduced: "AAF spec 1998; Premiere Pro export since CS era"
min_premiere_version: null
api_namespace: null
languages: [xml, python]
tags: [aaf, interchange, interop, davinci-resolve, avid, audio, roundtrip]
related: [xml-fcpxml, otio-interchange, premiere-to-resolve-handoff-guide, export-rendering-media-encoder]
sources: [
  "Adobe Premiere Pro AAF export documentation",
  "Blackmagic Design DaVinci Resolve manual (AAF conform)",
  "Community workflow reports (2025-2026)"
]
confidence: high
last_verified: "2026-07-14"
verified_against_version: "Premiere 25.6, Resolve 19+"
---

# AAF (Advanced Authoring Format) Interchange

## TL;DR

**AAF = binary interchange format, originally designed for Avid, now the de-facto standard for Premiere → DaVinci Resolve audio-heavy handoffs.** Carries clip cuts, timing, some effects/speed data, and audio — either embedded (Broadcast WAV inside the AAF) or linked (referenced media files alongside a lighter AAF). **Does NOT carry titles, graphics, MOGRTs, or Resolve-specific effects.** Reliability is version-dependent — community reports describe Premiere-authored AAF as "hardly ever works reliably" for anything beyond a straightforward audio/video cutlist; XML is often steadier for editorial-only structure.

---

## Export from Premiere Pro

`File → Export → AAF`

Key options:
- **Mixdown video** — checked: bakes all video tracks into one flattened clip (safest when the receiving app only needs picture reference, not editable tracks). Unchecked: keeps clips linked to their separate source files, editable in the target app.
- **Audio codec / embed choice** mirrors the same fork Resolve's own AAF export offers (see below) — embedded Broadcast WAV inside the AAF, or linked to separate media referenced by path.

---

## Import into DaVinci Resolve — Conform Behavior

Resolve treats an imported AAF/XML as a **conform** operation, not a plain import: it tries to relink every referenced clip against media already in (or added to) the Media Pool, by filename/reel/timecode matching. Source media must be delivered to the Resolve machine SEPARATELY — the AAF/XML file alone carries paths and metadata, never the actual media essence (unless "Embedded in AAF" was chosen for audio specifically — video is essentially never embedded).

**Verified gotchas (production-confirmed, 2025-2026):**

| Symptom | Cause | Fix |
|---|---|---|
| Audio splits into separate mono L/R tracks | Resolve's AAF/XML importer always demotes stereo to dual-mono tracks | Delete the redundant mono track, select the remaining clips, Clip Attributes → change Audio from Dual Mono to Stereo |
| Speed-changed clips play at wrong pitch, or the speed control is greyed out | A Premiere clip sped up without "Maintain Pitch" carries a locked pitch-correction flag into Resolve | Unlink (Alt-click) the clip to unlock Speed/pitch attributes, disable pitch correction manually |
| Some audio clips fail to relink | Filename/path mismatch, or codec Resolve's importer doesn't recognize from that export path | Verify exact filenames match Media Pool clips before conform; re-render mismatched sources to a standard codec (ProRes/DNxHR) if needed |
| Scaled clips render at the wrong size/crop | Premiere's "Scale to Frame Size" vs "Set to Frame Size" distinction doesn't translate — Resolve reads the raw transform | In Premiere, right-click affected clips → **Set to Frame Size** (not Scale to Frame Size) before export; in Resolve, Settings → Image Scaling → Input Scaling → **Center crop with no resizing** |
| General instability / missing elements on complex timelines | AAF from Premiere is reported as inconsistent on anything beyond a simple cutlist — nested sequences, many effects, or nonstandard track structures increase failure risk | For editorial-structure-only handoffs (no audio mixing needs), prefer XML (`xml-fcpxml.md`) or OTIO (`otio-interchange.md`) instead — steadier for pure cut/timing transfer. Reserve AAF for when you specifically need the audio mixing/sample-accurate handles Resolve's Fairlight page benefits from. |

---

## What AAF Preserves vs. Drops

| Element | Preserved | Notes |
|---|---|---|
| Clip cuts, in/out, track position | ✅ | Core purpose of the format |
| Audio (embedded or linked) | ✅ | Choice affects file size/portability, see above |
| Basic linear speed changes | ✅ | Pitch-lock gotcha applies, see table above |
| Sequence markers | ⚠️ | Partial — verify after conform, some marker metadata is known to drop |
| Titles / Essential Graphics / MOGRT | ❌ | Never transfers — see `premiere-to-resolve-handoff-guide.md`'s Graphics section for the required workaround |
| Premiere-native effects (Lumetri, most filters) | ❌ | AAF has no concept of Premiere's proprietary effect graph; only a small common subset (basic transform/opacity) survives in the best case, and should not be relied on |
| Nested sequences | ⚠️ | Unreliable — flatten nests before export when possible |
| Multicam sequences | ❌ | Not supported by the interchange model at all — flatten to a single cut before export |

---

## Practical Pre-Export Checklist (Premiere side)

1. Duplicate the sequence — never export your live working timeline.
2. Flatten/remove nested sequences.
3. Remove or pre-render (see graphics workflow) all titles, MOGRTs, Essential Graphics.
4. Remove color correction and non-essential effects — Resolve is where grading happens next; carrying Premiere-side color guesses into a fresh grade is counterproductive anyway.
5. `Set to Frame Size` (not Scale to Frame Size) on any manually scaled clips.
6. Re-render/replace any clip using a plugin-dependent effect or a speed change with special interpolation, since neither survives the interchange.
7. Export AAF; separately deliver every referenced source media file to the Resolve workstation.

---

## Cross-References

- `xml-fcpxml.md` — the lighter-weight alternative, often steadier for pure editorial structure.
- `otio-interchange.md` — newer, JSON-based alternative with native support in both apps as of late 2024/2025.
- `premiere-to-resolve-handoff-guide.md` — the full decision matrix (which format for which job) and the required graphics/titles workaround.

## Sources

- Adobe: Export AAF files — https://helpx.adobe.com/premiere-pro/using/export-aaf-files.html
- Blackmagic Design DaVinci Resolve Manual — AAF conform chapter
- Studio Network Solutions — Premiere↔Resolve roundtrip workflow guide
- MASV — Premiere Pro to DaVinci Resolve Workflow tutorial
- Production-facing community reports (Blackmagic Design forum, Creative COW), 2025-2026
