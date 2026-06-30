---
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
