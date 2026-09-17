---
id: premiere-to-resolve-handoff-guide
title: Premiere Pro → DaVinci Resolve Handoff — Full Playbook
category: workflow
status: current
stability: active
doc_status: complete
introduced: null
min_premiere_version: null
api_namespace: null
languages: [xml, python]
tags: [interop, davinci-resolve, aaf, xml, otio, mogrt, titles, graphics, roundtrip, conform]
related: [xml-fcpxml, aaf-interchange, otio-interchange, essential-graphics-mogrt-text, export-rendering-media-encoder]
sources: [
  "Adobe Premiere Pro AAF/XML/OTIO export documentation",
  "Blackmagic Design DaVinci Resolve manual",
  "Community workflow guides (Studio Network Solutions, MASV, VioletFlare), 2025-2026",
  "Production testing and community forum reports, 2025-2026"
]
confidence: high
last_verified: "2026-07-14"
verified_against_version: "Premiere 25.6, Resolve 19+"
---

# Premiere Pro → DaVinci Resolve Handoff — Full Playbook

## TL;DR

Three interchange formats move a Premiere edit into Resolve: **XML** (steadiest for pure editorial structure), **AAF** (best when Fairlight-side audio mixing needs sample-accurate handles, but reported as unreliable beyond a simple cutlist), **OTIO** (native in Resolve since 18.5, Premiere-side still Beta as of 2026-07, best suited to scripted pipeline steps rather than a one-off human handoff). **None of the three carry titles, Essential Graphics, MOGRTs, or app-specific effects — this is universal across all three formats, not a bug in any one of them.** The only reliable way to bring text/graphics across is to pre-render them as alpha-channel video and reintegrate as a plain overlay clip, or rebuild them natively in Resolve (Text+/Fusion). This doc is the decision matrix + the concrete graphics workaround; see `xml-fcpxml.md`, `aaf-interchange.md`, `otio-interchange.md` for per-format depth.

---

## Which Format, When

| Need | Use | Why |
|---|---|---|
| Straightforward picture edit, grading only | **XML** | Steadiest of the three for pure cut/timing structure; two decades of production mileage |
| Full sound mix needs to move to Fairlight with sample-accurate handles | **AAF** | Only one of the three modeling audio mixing needs directly — but flatten/simplify the timeline first, reliability drops fast on complex sequences |
| A scripted/automated pipeline step (shot list generation, automated conform, batch relinking) | **OTIO** | Clean JSON model, first-class Python library (`opentimelineio`), designed for exactly this; NOT the right pick for a one-off manual handoff given Premiere-side Beta status |
| Any handoff involving titles/graphics/MOGRTs | **Whichever of the above, PLUS the graphics workaround below** | No interchange format transports these — this is a separate problem from picking a format |

**Universal pre-flight, regardless of format chosen:**
1. Duplicate the sequence — never export the live working timeline.
2. Flatten nested sequences; flatten/pre-cut multicam sequences (none of the three formats support multicam).
3. Strip or pre-render all titles/graphics/MOGRTs (see below) — do this BEFORE export, not after.
4. Remove Premiere-side color correction — Resolve is where the grade happens next.
5. `Set to Frame Size` (not *Scale to* Frame Size) on any manually resized clips; in Resolve, set Input Scaling → Center crop with no resizing.
6. Deliver every referenced source media file to the Resolve workstation separately — the interchange file carries paths/metadata, essentially never the actual media.
7. After conform in Resolve: check audio tracks (all three formats/importers split stereo into dual mono — fix via Clip Attributes) and verify markers survived.

---

## Why Graphics/Titles Never Transfer (Root Cause)

This isn't a missing feature in any one format — it's structural. Premiere's Essential Graphics / MOGRT system is built on After Effects' text-layer object model, serialized as either a proprietary binary FlatBuffer (Premiere 2024+) or, for Premiere-authored graphics, an internal representation with no public schema at all (see `essential-graphics-mogrt-text.md`). XML, AAF, and OTIO all model **editorial structure** — clips, cuts, timing, tracks, basic transforms — none of them define a shared vocabulary for "a text layer with this font, this animation curve, this Essential Graphics parameter set." DaVinci Resolve has its own, entirely separate graphics system (Text+ / Fusion Titles) with zero object-model overlap with Premiere's. There is no missing checkbox or export setting that fixes this — the two graphics systems are simply incompatible at the data level, not just the file-format level.

---

## The Working Solution: Pre-Render With Alpha, Reintegrate as an Overlay

This is the industry-standard workaround, confirmed across every source consulted for this doc. Two variants depending on whether the graphic needs to remain editable downstream.

### Variant A — Burn-in (final text, no further editing needed)

1. In Premiere, select the graphic/title clip(s). Isolate them onto their own video track(s), above the picture.
2. `File → Export → Media`. Format: **QuickTime**, Codec: **Apple ProRes 4444** (Mac) or **DNxHR 444 12-bit** (Windows) — these are the practical, broadly-compatible options that carry a true RGBA alpha channel (Animation and GoPro CineForm also support alpha and are viable alternatives).
3. Enable **Export Alpha Channel**. Choose **Straight alpha** unless you have a specific reason to use premultiplied — mismatching straight/premultiplied between export and the compositing app is the single most common cause of dark/light fringing around text edges after reimport.
4. Export at the SAME resolution and frame rate as the sequence, matching in/out exactly to the source graphic clip's timeline position (export just that clip's range, or the whole sequence range and trim afterward).
5. Deliver the resulting alpha-channel .mov alongside the rest of the media for the Resolve conform.
6. In Resolve, place the alpha clip on its own video track above the graded picture, positioned to match the original timing (the XML/AAF/OTIO conform will usually NOT auto-place it — it wasn't part of the interchange data at all, since it didn't exist as a distinct entity in Premiere's export in the first place unless you left the ORIGINAL graphic clip in place as a gap-filler reference for manual repositioning).

**Practical tip:** before stripping graphics from the export sequence, note each one's exact timeline position (or leave a plain-color placeholder clip of the same duration/position in the exported timeline) so re-placing the alpha overlay in Resolve is a simple drag-to-match rather than guesswork.

### Variant B — Rebuild Natively in Resolve (needs further editing/animation control downstream)

If the graphic needs to stay editable (translate captions, adjust timing after grading, client wants copy changes), pre-rendering bakes it in — not appropriate. Instead:
- Rebuild the text using Resolve's **Text+** node (Fusion page) for anything reasonably simple — font, size, position, basic animation.
- For anything closer to a genuine MOGRT-style templated graphic (reusable across many shots with swappable text), build a **Fusion template/Macro** or a **PowerGrade-equivalent** on the Edit page's Effects Library — this is the closest Resolve equivalent to a reusable MOGRT, though the authoring workflow is materially different (node-based Fusion compositing vs. Premiere's Essential Graphics panel) and is not a drop-in swap; budget real rebuild time, not just a reimport.
- There is no automated conversion path from an .mogrt file into a Fusion template — confirmed no such tool exists; this is manual recreation work.

### Variant C — Images (photos, logos, stills)

Static images (no text, no animation) are the one case that's straightforward: PNG/TIFF with alpha (or plain JPEG if no transparency is needed) placed as project items transfer through the interchange formats like any other media clip, since Resolve's conform just needs to relink a file by name — deliver the image files alongside the rest of the media and they'll conform normally. This is NOT the same problem as titles/MOGRTs; only text/graphic-LAYER objects (Essential Graphics, titles, MOGRTs) have the transfer problem described above. A still image used as a source clip is just a source clip.

---

## Full Decision Flow

```
Need to move an edit to Resolve?
├─ Does the timeline contain titles/MOGRTs/Essential Graphics?
│   ├─ Yes → pre-render each as alpha .mov (Variant A) BEFORE export,
│   │        or plan to rebuild in Resolve (Variant B) if they must stay editable
│   └─ No  → skip straight to format choice
│
├─ Just images/photos/logos, no text layers? → they transfer fine as normal
│   media, no special handling needed (Variant C)
│
└─ Pick interchange format:
    ├─ Pure picture edit, going to grade only        → XML
    ├─ Full audio mix needs Fairlight, simple timeline → AAF
    ├─ Scripted/automated pipeline step                → OTIO
    └─ Complex timeline + full audio mix               → XML first (steadier),
                                                           handle audio separately
                                                           if AAF proves unreliable
```

---

## Cross-References

- `xml-fcpxml.md` — FCP7 XML format detail, structure, parsing.
- `aaf-interchange.md` — AAF format detail, audio embed/link choice, known gotchas.
- `otio-interchange.md` — OTIO format detail, current Beta status on the Premiere side.
- `essential-graphics-mogrt-text.md` — why Premiere's own MOGRT text format is already a binary FlatBuffer with no public schema, the root cause underlying why it can't cross into any interchange format either.

## Sources

- Adobe: Export AAF files — https://helpx.adobe.com/premiere-pro/using/export-aaf-files.html
- Adobe Community — OTIO Import/Export Beta announcement
- Blackmagic Design DaVinci Resolve manual — conform, Text+/Fusion titles, alpha export
- Studio Network Solutions — Premiere↔Resolve roundtrip workflow guide
- MASV — Premiere Pro to DaVinci Resolve Workflow tutorial
- Frame.io blog — alpha export codec guidance
- Blackmagic Design community forum — motion graphics conversion discussion threads
