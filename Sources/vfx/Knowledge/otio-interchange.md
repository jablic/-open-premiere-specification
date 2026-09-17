---
id: otio-interchange
title: OpenTimelineIO (OTIO) Interchange
category: interop
status: current
stability: beta-on-premiere-side
doc_status: complete
introduced: "Premiere Pro Beta, Oct 2024 (export/import); DaVinci Resolve native since 18.5"
min_premiere_version: "Beta channel only as of 2026-07"
api_namespace: null
languages: [json, python]
tags: [otio, opentimelineio, interchange, interop, davinci-resolve, pipeline]
related: [xml-fcpxml, aaf-interchange, premiere-to-resolve-handoff-guide, automation]
sources: [
  "Adobe Premiere Pro Beta community announcement (OTIO import/export release)",
  "OpenTimelineIO project documentation (Academy Software Foundation)",
  "DaVinci Resolve manual (OTIO import)",
  "Community workflow reports (2025-2026)"
]
confidence: high
last_verified: "2026-07-14"
verified_against_version: "Premiere Pro Beta (Oct 2024+), Resolve 18.5+"
---

# OpenTimelineIO (OTIO) Interchange

## TL;DR

**OTIO = open-source, JSON-based timeline interchange format from the Academy Software Foundation, built for VFX/animation pipelines rather than picture-lock delivery.** Adobe added Premiere Pro export/import support in the **Beta** channel starting October 2024 — as of 2026-07 it has **not graduated to the general release build**, Adobe's own framing is that it hasn't yet reached "release standard" quality. DaVinci Resolve has had **native** OTIO import/export built into the timeline menu since **v18.5**, maturing with each release since. Like AAF and XML, **OTIO does not carry titles, graphics, MOGRTs, or app-specific effects** — it is a pure structural/timing interchange.

---

## Version & Access

| App | Support | Where |
|---|---|---|
| Premiere Pro | Beta only (Oct 2024+), not in general release as of 2026-07 | `File → Export → OpenTimelineIO`; import via `File → Import` or Media Browser |
| DaVinci Resolve | Native since 18.5, improving each release | Timeline menu (export), File → Import Timeline (import), also accepts `.otioz` (zipped, bundles media references) |

If you're on Premiere's general-release (non-Beta) build, OTIO is simply not available yet — fall back to XML or AAF.

---

## What Premiere's OTIO Export Includes

- Clip names, cutlist with clips positioned correctly in the sequence
- Source in/out points, durations, starting timecode
- Frame rate, sequence frame size, sample rate
- Multiple video/audio tracks, with track names
- Linear speed adjustments
- Sequence markers (start, duration, name, color) and clip markers (start, duration, name, comment, color) — round-trips reasonably well

## What It Excludes / Known Limitations

- **Titles, Essential Graphics, MOGRTs — never included**, same as AAF/XML (see `premiere-to-resolve-handoff-guide.md` for the workaround).
- **Multicam sequences are not supported** at all — flatten before export.
- Clip metadata fields (Tape Name, Description) are not exported.
- Clip names can revert to source filenames after a full Premiere → OTIO → Premiere round trip.
- Media file path handling has shown inconsistency across systems/platforms in community testing.
- On the Resolve import side: Resolve-specific and most third-party effects never transfer (expected — OTIO has no effect-graph model shared across apps). Complex transitions frequently collapse to plain cuts; only basic dissolves reliably survive. Track names often revert to generic labels ("Video 1", etc.) and need manual relabeling.
- Community consensus as of 2025-2026: **XML remains the more robust choice for interchange today** — OTIO is actively improving but younger and rougher at the edges for this specific Premiere↔Resolve path than the two decades-old FCP7 XML format.

---

## When to Actually Use OTIO (vs XML/AAF)

OTIO's real strength is **scriptable pipeline integration** — it's a first-class Python library (`pip install OpenTimelineIO`) with adapters for a growing list of NLEs, and is the natural choice when a VFX/pipeline tool needs to read or rewrite timeline structure programmatically (shot lists, conform reports, automated relinking) rather than round-trip through an NLE's own UI. For a one-off human-driven Premiere → Resolve handoff, XML or AAF are currently steadier. For a repeated, scripted, multi-tool pipeline step, OTIO's clean JSON model and Python tooling are usually worth the current rough edges.

```python
import opentimelineio as otio

timeline = otio.adapters.read_from_file("sequence.otio")
for track in timeline.tracks:
    print(track.name, track.kind)
    for clip in track:
        if isinstance(clip, otio.schema.Clip):
            print(" ", clip.name, clip.source_range)
```

---

## Cross-References

- `xml-fcpxml.md` — the steadier, older alternative for pure editorial structure.
- `aaf-interchange.md` — the audio-mixing-focused alternative, with its own gotchas.
- `premiere-to-resolve-handoff-guide.md` — full decision matrix and the required graphics/titles workaround (applies identically regardless of which of the three interchange formats is used).

## Sources

- Adobe Community — "[Now Released] OTIO Import and Export" (Premiere Pro Beta announcement)
- OpenTimelineIO project (Academy Software Foundation) — https://opentimelineio.readthedocs.io/
- Blackmagic Design DaVinci Resolve manual — OTIO import chapter
- Larry Jordan — "OpenTimelineIO – What It Is and What It Does"
- VioletFlare — "DaVinci Resolve OTIO Import: What It Is and How to Use It"
