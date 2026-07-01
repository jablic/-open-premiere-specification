---
id: glossary
title: Glossary - Terms & Definitions
category: reference
status: current
stability: active
doc_status: complete
introduced: "2026"
min_premiere_version: null
api_namespace: null
languages: null
tags: [glossary, terminology, reference, definitions]
related: [premiere-dom-overview, extendscript-core, uxp, cep, reverse-engineering-qe-dom]
sources: []
confidence: high
last_verified: "2026-06-30"
verified_against_version: "25.6"
---

# Glossary - Terms & Definitions

## TL;DR

Quick-reference definitions for terms used throughout this Knowledge Base. Cross-links point to the full doc covering each concept.

---

## A

**AEGP (After Effects General Plugin) Suite** — Set of APIs exposed by After Effects for native plugins. Premiere does NOT have AEGP suites; video filters built on AE SDK run in a more limited context. See `cpp-native-sdk.md`.

**ASE (Angle Switcher / Multicam Editor)** — UI tool for live camera-cut editing in multicam sequences. No scripting API. See `multicam-api.md`.

**AME (Adobe Media Encoder)** — Standalone encoding application that Premiere can queue exports to. See `export-rendering-media-encoder.md`.

---

## C

**CEP (Common Extensibility Platform / Chromium Embedded Framework)** — Legacy panel framework using Chromium + HTML5 + ExtendScript bridge. Deprecated, last runtime CEP 12 (Premiere 25.0). See `cep.md`.

**CSInterface** — JavaScript bridge object used in CEP panels to call `evalScript()` against ExtendScript. See `cep.md`.

**CTI (Current Time Indicator)** — The playhead position in the timeline.

---

## E

**ExtendScript** — Adobe's legacy scripting language, ECMAScript 3 (ES3) based. EOL September 2026. See `extendscript-core.md`.

**executeTransaction()** — UXP method required to wrap any DOM mutation (timeline edits) for proper undo/redo support. See `uxp.md`.

---

## F

**FCP7 XML / FCPXML** — Final Cut Pro 7 interchange XML format, used for cross-application timeline exchange (e.g. with DaVinci Resolve). See `xml-fcpxml.md`.

---

## L

**Lumetri Color** — Premiere's primary color grading effect/panel. Parameters accessible via component properties, but names/IDs are undocumented and version-fragile. See `color-management.md`.

**LUT (Look-Up Table)** — Color transform file (.cube format common) applied via Lumetri Input LUT parameter.

---

## M

**MOGRT (Motion Graphics Template)** — Animated graphic template (.mogrt file) importable into Premiere with editable Source Text and parameters. See `essential-graphics-mogrt-text.md`.

**Multicam Sequence** — A nested Sequence object containing multiple synced camera angle tracks. No distinct API class; behaves as a regular Sequence once created. See `multicam-api.md`.

---

## P

**.prproj** — Premiere project file format (proprietary, binary/XML hybrid, undocumented structure). No supported direct-parsing API. See `project-file-format.md`.

**PrSDK (Premiere Pro SDK)** — C++ SDK for native plugins (exporters, importers, playback engines). Video filters require AE SDK in addition. See `cpp-native-sdk.md`.

---

## Q

**QE DOM (Query Engine DOM)** — Undocumented internal scripting bridge (`app.qe`) exposing functionality absent from the public API: effects-by-name, ripple edits, speed changes, frame export. See `reverse-engineering-qe-dom.md`.

---

## T

**Tick** — Premiere's internal time unit. 254,016,000,000 ticks per second. Used internally by Time objects and XML interchange formats. See `sequences-tracks-trackitems.md`.

**Time Object** — ExtendScript/UXP object representing a time value, required for accurate timing operations since Premiere 14.1+.

**TrackItem** — DOM object representing a single clip instance placed on a timeline track (distinct from ProjectItem, which represents the source media). See `premiere-dom-overview.md`.

---

## U

**UDT (UXP Developer Tool)** — Modern debugging tool for UXP plugins, analogous to browser DevTools. See `uxp.md`.

**UXP (Unified Extensibility Platform)** — Modern, async-first plugin platform; general release in Premiere 25.6. Recommended for all new development. See `uxp.md`.

---

## Z

**ZXP** — Signed/packaged extension format for CEP panels. Required signing mandatory on macOS 25.2.3+. See `security-signing.md`.

---

See also: premiere-dom-overview.md, decision-trees.md
