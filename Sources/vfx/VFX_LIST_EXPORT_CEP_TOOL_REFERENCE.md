---
id: vfx-list-export-cep-tool-reference
title: VFX List Export — CEP Tool Complete Feature Reference
category: tool-reference
status: current
stability: active
introduced: "2026 (formerly ShotifyFlex)"
languages: [extendscript, javascript, html]
tags: [vfx-list-export, shotifyflex, cep, premiere-pro, markers, captions, mogrt, text-plates, automation]
related: [captions, essential-graphics-mogrt-text, reverse-engineering-qe-dom, timeline-operations-complete]
confidence: high
last_verified: "2026-07-14"
verified_against_version: "25.6 / 26.x, tool v0.7.80"
---

# VFX List Export — Complete Feature Reference

## What This Is

A production CEP panel for Adobe Premiere Pro, real name **"VFX List Export"** (formerly **ShotifyFlex**). Manages a VFX/CG pipeline directly from the timeline: generates shot lists with thumbnails/reference movies, converts between markers/captions/text-plates, batch-renames/renumbers shots by a configurable ID mask, and re-imports rendered deliverables back onto the timeline.

**This is NOT** the abandoned UXP prototype (`vfx-list-uxp-panel/` in the `-open-premiere-specification` repo, or the various `VFX_TOOL_*.md`/`README_VFX_TOOL_OPTIONS.md`/`QUICK_START.md` docs describing it) — that was an early, separate exploration and is not the tool in active production use.

**Install location (active):** `~/Library/Application Support/Adobe/CEP/extensions/VFX List Export/`
**Install location (stale, do not confuse):** `/Library/Application Support/Adobe/CEP/extensions/com.shotifyflex.panel/` — a system-level ZXP install, was several versions behind as of this writing (v0.7.68 vs the active copy's v0.7.80). Confirm the panel header's version number against `CSXS/manifest.xml` before assuming which copy is running.
**Source layout:** `index.html` (UI) + `js/main.js` (panel logic, CEP/CEF side) + `jsx/host.jsx` (ExtendScript, runs inside Premiere's engine) + `bridge/*.py` (Python helpers for xlsx/mogrt baking, invoked as subprocesses) + `presets/*.mogrt`/`*.epr` (bundled templates).

**Critical dev gotcha:** `host.jsx` is loaded into Premiere's ExtendScript engine ONCE per session — editing it on disk mid-session does NOT hot-reload. A full Premiere quit+relaunch is required after any `host.jsx` change; `main.js`/`index.html` (CEF/HTML side) DO reload on panel close/reopen. The panel has a built-in staleness detector (`shotifyHostVersion()` vs the manifest version) that shows a banner if these ever get out of sync — usually means the internal `HOST_JSX_LOADED_VERSION` constant wasn't bumped alongside the manifest.

---

## Block 1 — VFX List

Generates the shot list itself (the core deliverable) — an exportable spreadsheet/report with shot IDs, timecodes, metadata, and optional thumbnails.

**Source ("VFX names from…"):** Timeline markers / Timeline Captions / Timeline Text-plates / External Subtitles (.srt).

**ID mode:**
- *Use text from source* — the shot ID is whatever text is already on the marker/caption/plate.
- *Generate from mask + step* — ignores source text, assigns sequential IDs from a `####`-style mask + Start/Step, in source order.

**Marker-source-only filters** (when Source = Timeline markers):
- Marker field: Name or Comments.
- Marker color filter — multi-select swatch picker; auto-detects and pre-checks whichever color is most common on the timeline (assumed to be "the" shot-marker color, filtering out one-off comment markers of other colors).
- Remove empty markers (no name & no comment).
- Merge markers at the same timecode (combines multiple markers sharing a start frame into one entry).
- **Its own TC IN–OUT range** (`markerRangeEnabled`/`markerRangeIn`/`markerRangeOut`) — independent of Block 3's and Block 4's own range pickers (three separate, non-interacting range controls in this tool — see "TC Range Mechanic" below).

**Columns:** a large configurable checklist (Episode, Scene, PRMST, Task, Duration, References, HIREZ SOURCE, Vendor, TC in/out, Status, Star, Deadline, Source In/Out, Frame Rate, Source Path, Frame Size, Comments, Track, Reel, etc.), with three one-click presets: **Turnover**, **Technical**, **Review**. Any hand-edited combination shows as "Custom".

**Fast table scan** — skips Source In/Out and other source-metadata-heavy columns for speed when only shot IDs/timecodes/workflow columns are needed.

**Thumbnails** — size presets (Medium/500×270/720×480/Custom), frame position (first/middle of shot), output folder, image format (JPG/PNG/GIF). Stills are generated ONCE per shot and reused on subsequent exports; "Force re-export thumbnails" is the explicit escape hatch after re-cutting shots.

**Export format:** Excel (.xlsx, embedded stills), CSV, TXT (tab-separated), HTML (visual with thumbnails), PDF (with thumbnails).

**Buttons:** *Scan / preview* (read-only) and *Export VFX list* (writes the report file).

---

## Block 2 — Video References

Exports per-shot reference movies (and, via shared checkboxes with Block 1, thumbnails) for review.

- Reference preset (.epr, bundled `vfx_prmst.epr` by default), output folder, extension.
- Export engine: *From Timeline* (direct) or *Adobe Media Encoder queue*.
- Single button: **Export shots**.

---

## Block 3 — Convert

Converts shot data between the three timeline-native representations (Markers / Captions / Text-plates), any of the 6 meaningful directed pairs, through one shared From/To control with a swap button.

**Source-specific options:**
- Markers → Marker field (Name/Comments).
- Captions → read from Timeline Captions track, or an external .srt file.
- Text-plates → track picker (Auto-detect or explicit V-track).

**Destination-specific options:**
- **→ Markers:** marker color for the newly created markers.
- **→ Captions:** Output .srt path; "Also build native caption track" checkbox — if checked, imports the .srt and calls `Sequence.createCaptionTrack()` to place it live on the timeline (no manual re-import step). See "Captions API Reality" below for the hard limits on this.
- **→ Text-plates:** Plate type (Editable MOGRT or Rendered PNG), Position (6 presets: top/bottom × left/center/right), target track. A shared style panel (font, size, scale, bold/italic/background/stroke, text/background/stroke color) — **for Editable MOGRT, only Font and the text itself actually get patched**; Size/Scale/Bold/Italic/Stroke/Text Fill are baked into the MOGRT template at build time and can't be overridden per-clip (a structural limitation of the binary Source Text format, not a bug — see `essential-graphics-mogrt-text.md`). Rendered PNG has full control over all of these since it's not constrained by the MOGRT format.
  - Advanced: custom MOGRT template override (default: auto-picks one of 6 bundled position-matched templates, `presets/cg_name_<position>.mogrt`).

**TC IN–OUT range (v0.7.80+):** own independent checkbox + TC In/TC Out fields (`convRangeEnabled`/`convRangeIn`/`convRangeOut`), auto-filled from the sequence's Mark In/Mark Out with a live status indicator, same mechanic as Block 4's (see below) but a fully separate instance — only items whose start falls inside this range get converted, regardless of what Block 4's own range is set to.

**Button label is dynamic:** shows the actual direction, e.g. "Markers → Text-plates".

---

## Block 4 — Rename & renumber

Batch-renames/renumbers existing shots by a configurable mask pattern. Operates independently of Block 1's source selection — has its own "What to rename" picker.

**What to rename:** Markers / Captions (auto-detect from timeline) / Text-plates / Captions (external .srt file).

**TC IN–OUT range** (`renumberRangeEnabled`/`renumberRangeIn`/`renumberRangeOut`) — same UI pattern as Block 1's and Block 3's, own independent instance. Live status line shows one of: `✓ Range active (from Mark In/Mark Out): ...`, `✓ Range active (from Work Area bracket): ...`, `✓ Range active (from "IN"/"OUT" markers): ...`, or a ⚠ warning naming which of the three sources came back empty/degenerate. See "TC Range Mechanic" below for the full 3-tier detection.

**New Shot ID pattern:** Project prefix, Episode №, Scene №, Shot type, Shot number padding (digits), assembled client-side into a mask string like `OTV_EP02_CG01_####` (any field left blank is dropped from the ID entirely, not replaced with a placeholder). Start / Step for the sequential numbering.

**Live "RESULT: …" preview (v0.7.80+):** shows what the first shot's ID (using the Start value) will actually come out as, recomputed on every keystroke in any mask-feeding field — pure client-side mirror of `host.jsx`'s `applyMask()`, no host round-trip.

**Markers-only actions** (when "What to rename" = Markers):
- "Extend markers to clip duration from: [track]" — optional add-on that first snaps each point (zero-duration) marker to the underlying clip's full boundaries on the chosen track, then renames. Only ever touches point markers, safe to re-run.
- "Set marker color to: [color]".
- Button: **Rename Timeline Markers**.

**Text-plates-only:**
- "Also rename project items" — renames the Project panel bin label (timeline clip names are read-only in Premiere's scripting API, so this is the closest available substitute — does NOT change the clip's own displayed name nor the visible on-screen text).
- Button: **Rebuild text-plates** — the *actual* way to change what's visibly rendered: bakes a brand-new .mogrt per shot (same builder as Convert) and REPLACES each existing plate clip in place, same track, same in/out. Full clip swap, not a text patch — any effects/opacity keyframes/trims on the old clip are lost, only position/timing/text carry over. (A now-removed "Rewrite plate text (experimental)" in-place patch attempt was dropped in v0.7.76 — it empirically failed on every real test, superseded entirely by this rebuild approach; see `essential-graphics-mogrt-text.md`'s FlatBuffer notes for why.)

**Captions-only:**
- Button: **Rebuild subtitles** — same rebuild philosophy as text-plates, adapted to captions' different constraint (no per-entry write API exists at all, only whole-track `createCaptionTrack()` — see "Captions API Reality"). First TRIES to remove the old caption track via undocumented QE methods, verified by re-reading the track count; if that succeeds, this is a genuine single-track replacement (in-range renamed + out-of-range carried over unchanged). If QE removal isn't available on the current Premiere build, falls back to adding a new track containing ONLY the in-range renamed entries (old track left alone, no duplicates for the untouched portion, but the old track's stale in-range entries need manual trim/delete). The result message states which of the two actually happened.

**Shared actions (any source):**
- Mapping CSV path — every Renumber/Rebuild click writes an Old ID → New ID → TC In audit trail here, even in preview.
- **Check conflicts** — read-only audit: duplicate IDs, empty IDs, mask mismatches, out-of-order sequencing.
- **Renumber** — writes new IDs back to the source. For Markers/Captions this is a direct, meaningful rename. **For Text-plates specifically, with both checkboxes above unchecked, this does almost nothing visible** — it only writes the Mapping CSV, since timeline clip names are read-only and there's no other target to write to (this is the tool's most commonly misunderstood control; see the in-panel warning text next to "Also rename project items").
- **Revert last renumber (from map)** — since ExtendScript has no undo-group API at all (confirmed via Adobe's developer forum — nothing this panel writes ever reaches Premiere's own Edit ▸ Undo stack, on any version), this is the real substitute: re-reads the Mapping CSV, finds whatever currently matches each NewID, and renames it back to OldID. Only undoes what's still in the file and hasn't been renamed again since — not a true undo.

---

## Block 5 — Import and check

Re-imports rendered deliverables back onto the timeline as a QC pass.

**Import mode:**
- *Import PRMST (by embedded timecode)* — re-imports Block 2's exported reference movies onto a brand-new video track, at each file's own EMBEDDED start timecode (read from the file itself, not replayed from this plugin's export log). Confirms references land exactly where expected and at full resolution.
- *Import Hirez mov (match by filename)* — for hi-res deliverables from an EXTERNAL tool (e.g. DaVinci Resolve) whose embedded timecode is the original camera source TC, not the timeline's own (so embedded-TC placement would be wrong). Instead matches each file's NAME against the current Shot IDs (any vendor tag/version/pass-name prefix/suffix around the matched ID is ignored) and places it at that shot's timeline position. Files sharing the same matched Shot ID are treated as separate layers and auto-stacked on their own new tracks.
  - Match against: Timeline markers / Subtitles (.srt) / Text-plates.
  - "Has handles" — trims a configurable head/tail frame count off each hi-res file's own source range before placement, for files that run long at the start/end.

**Place on track:** Auto (always adds new track(s) above everything) or a specific existing track as the base.

**Import from folder** — defaults to Block 2's own export output folder; picks up .mp4/.mov/.mxf/.m4v/.avi automatically.

**Button:** **Import and check**.

---

## Results Panel

Shared status area (right column): progress bar, status box, a results table for structured output (e.g. per-shot audit rows), and a collapsible Process log (with Copy) for the full verbose trace — the place to look when a result message alone isn't enough to diagnose a "why did this skip N shots" question.

---

## TC Range Mechanic (Cross-Cutting)

**Three fully independent range pickers exist** — Block 1 (marker-source scan filter), Block 3 (Convert), Block 4 (Rename & renumber) — each with its own checkbox + TC In/TC Out fields + config keys (`markerRange*` / `convRange*` / `renumberRange*`). Setting one does NOT affect the others.

**Detection is 3-tier, in priority order** (`shotifySequenceInOut()` in `host.jsx`):
1. **Sequence In/Out points** — what "Mark In"/"Mark Out" (`I`/`O` keys, or Markers menu → Mark In/Mark Out) actually sets. `getInPointAsTime()`/`getOutPointAsTime()`.
2. **Work Area bracket** — a SEPARATE, opt-in range, disabled by default (must explicitly enable "Work Area Bar" in the sequence's own hamburger menu). `getWorkAreaInPointAsTime()`/`getWorkAreaOutPointAsTime()`/`isWorkAreaEnabled()`.
3. **Point markers literally named "IN" and "OUT"** (case-insensitive) — a common editorial convention fallback when neither of the above is used. These two markers are automatically excluded from every marker-source shot list (never treated as a real shot themselves).

Whichever tier succeeds first populates TC In/TC Out and is labeled in the live status line (`(from Mark In/Mark Out)` / `(from Work Area bracket)` / `(from "IN"/"OUT" markers)`).

**Degenerate-range guard:** if a range is enabled but comes back empty (0/0, or TC Out ≤ TC In — the common symptom of nothing actually being marked), the tool does NOT silently drop the entire result set. It treats this as "no range" (uses everything) and surfaces an explicit ⚠ warning in both the live status hint (before you click) and the result message (after) — never a silent "0 shots found."

**Known persistence gotcha (fixed v0.7.75):** these range fields must NEVER be restored from the per-project sidecar config on panel reopen — a saved value (even an innocuous "00:00:00:00") permanently blocks the live-sync mechanism that would otherwise refresh them from the actual timeline every session. All six range-field IDs across the three blocks are excluded from config restore for this reason (`CONFIG_RESTORE_EXCLUDE` in `main.js`).

---

## Captions API Reality (Confirmed 2026-07)

Read separately in `Knowledge/captions.md` (this repo) for full detail; summarized here as it directly shapes Block 3/Block 4's Captions options:

- **No write API exists for a live Captions track at all** — confirmed by Adobe directly (community forum, Bruce Bullis): *"There is no API access to caption tracks... won't be available until PPro moves to UXP-based extensibility; no dates available."*
- The only write path is **whole-track replacement**: build a corrected `.srt` → import it → `Sequence.createCaptionTrack(item, 0, format)`.
- `createCaptionTrack()` only ever **ADDS** a track — no documented replace/remove counterpart. A best-effort, unverified QE escape hatch exists (see `reverse-engineering-qe-dom.md`) but isn't guaranteed on every Premiere build.
- Consequence: true range-scoped, in-place caption editing has a structural ceiling in this tool — "Rebuild subtitles" gets as close as currently possible (see Block 4 above) but documents the remaining manual step honestly rather than pretending it away.

---

## MOGRT / Text-Plates Reality

Read separately in `Knowledge/essential-graphics-mogrt-text.md` for the underlying FlatBuffer/binary format detail. Summarized here:

- Timeline clip names are read-only via the scripting API — "Also rename project items" (bin label) is the closest available substitute, not equivalent.
- Premiere 2026 stores an AE-authored MOGRT's Source Text as a binary FlatBuffer, not the legacy JSON `TextDocument` — in-place text patching is fragile-to-broken depending on build; this tool dropped its "Rewrite plate text (experimental)" attempt entirely (v0.7.76) after it failed every real test, in favor of the reliable **Rebuild text-plates** full-clip-swap approach.
- Only Font and the text itself are patchable into an Editable MOGRT at build time — everything else (size, scale, bold, italic, stroke, fill color, background) is baked into the template and requires either editing the template directly in Premiere, or switching to Rendered PNG for full per-shot control.

---

## Version History (This Session, 2026-07-13/14)

| Version | Change |
|---|---|
| v0.7.72 | Silent degenerate-TC-range guard (pre-existing since v0.7.63) made loud — surfaces `shotifyLastRangeIgnored` as a ⚠ warning instead of silently renaming the whole timeline. |
| v0.7.73 | 3-tier range detection added (Sequence In/Out → Work Area → named "IN"/"OUT" markers), with per-tier diagnostic dump. |
| v0.7.74 | Corrected terminology: earlier code mislabeled Sequence In/Out as "Work Area" — verified against official docs, fixed throughout. |
| v0.7.75 | Root-caused and fixed the REAL "range never updates" bug: stale sidecar-restored values permanently blocked the live-sync guard; checkbox restore didn't re-trigger the sync loop either. Both fixed. |
| v0.7.76 | Removed "Rewrite plate text (experimental)" (proven non-functional); "Rebuild text-plates" moved below the mask fields it consumes, renamed for clarity. |
| v0.7.77 | Added "Rebuild subtitles" (Captions equivalent of Rebuild text-plates), merge-based first version. |
| v0.7.78 | Fixed v0.7.77's out-of-range caption duplication bug — rebuilt track now contains only the in-range entries. |
| v0.7.79 | Added best-effort, verified QE-based old-caption-track removal for a true single-track replacement when available. |
| v0.7.80 | Added Block 3's own independent TC range (mirroring Block 4's); added Block 4's live "RESULT: …" mask preview. |

---

## Cross-References

- `captions.md` — full Captions API reality, formats, export.
- `essential-graphics-mogrt-text.md` — MOGRT FlatBuffer internals, workarounds.
- `reverse-engineering-qe-dom.md` — QE DOM, `qe.reflect.methods` discovery technique, undocumented track removal.
- `timeline-operations-complete.md` — Sequence In/Out vs. Work Area, corrected terminology.
