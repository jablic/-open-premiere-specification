# Open Premiere Pro Specification

[![Validate KB](https://github.com/jablic/-open-premiere-specification/workflows/Validate%20Knowledge%20Base/badge.svg)](https://github.com/jablic/-open-premiere-specification/actions)
[![Knowledge Base](https://img.shields.io/badge/Knowledge%20Base-20%20docs-brightgreen)](./Knowledge)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)](./PROJECT_SPECIFICATION.md)

Machine-readable knowledge base for Adobe Premiere Pro extensibility, automation, and development.

**Target:** AI coding agents (Claude, others)  
**Format:** Markdown + YAML frontmatter  
**Coverage:** ExtendScript, CEP, UXP, QE DOM, Export, Media Encoder, VFX workflows

---

## Quick Start

### For AI Agents

1. Clone repo and browse `Knowledge/` directory
2. Each file has YAML frontmatter: `status`, `doc_status`, `confidence`, `min_premiere_version`
3. Use `Examples/` as production-ready code templates

### For Humans

- **Project spec:** See `PROJECT_SPECIFICATION.md`
- **Technology matrix:** `Knowledge/00-technology-status-matrix.md`
- **Scripting guide:** `Knowledge/uxp.md` (modern) or `Knowledge/extendscript-core.md` (legacy)

---

## Knowledge Base (20 docs)

**Core Extensibility (5):** extendscript-core, cep, uxp, reverse-engineering-qe-dom, cpp-native-sdk

**Automation (5):** automation, export-rendering-media-encoder, essential-graphics-mogrt-text, sequences-tracks-trackitems, xml-fcpxml

**Reference (10):** premiere-dom-overview, best-practices, ai-integration, panels, import, markers, captions, debugging, examples-index, 00-technology-status-matrix

---

## Production Examples (6 files)

**ExtendScript (4):** batch-export-guarded, update-mogrt-text, cep-bridge-safe, qe-safe-wrapper

**UXP (2):** list-sequences, batch-effects-captions

**Python (1):** parse_premiere_fcpxml

---

## Status & Roadmap

| Premiere | ExtendScript | CEP | UXP |
|---|---|---|---|
| 24.x | Frozen | CEP 11 | Beta |
| 25.0–25.6 | Frozen | CEP 12 | **GA** |
| 26.0+ | **EOL Sept 2026** | Deprecated | Current |

---

## CI/CD

Automated validation on push/PR via `.github/workflows/validate.yml`

---

**Last updated:** 2026-06-30  
**Tested on:** Premiere 25.6
