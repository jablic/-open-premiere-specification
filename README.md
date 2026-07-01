# Open Premiere Pro Specification

[![Validate KB](https://github.com/jablic/-open-premiere-specification/workflows/Validate%20Knowledge%20Base/badge.svg)](https://github.com/jablic/-open-premiere-specification/actions)
[![Knowledge Base](https://img.shields.io/badge/Knowledge%20Base-37%20docs-brightgreen)](./Knowledge)
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

## Knowledge Base (40 docs)

**Core Extensibility (5):** extendscript-core, cep, uxp, reverse-engineering-qe-dom, cpp-native-sdk

**Automation (7):** automation, export-rendering-media-encoder, essential-graphics-mogrt-text, sequences-tracks-trackitems, xml-fcpxml, captions, import

**Workflow & Integration (5):** ai-integration, markers-and-annotations, media-linking-batch-operations, ui-theming-and-responsive-panels, best-practices

**Reference (8):** premiere-dom-overview, panels, debugging, examples-index, 00-technology-status-matrix, markers, captions (legacy stub), decision-trees

**Deep Dives & Advanced (15):** performance-optimization, migration-extendscript-to-uxp, migration-cep-to-uxp, security-signing, audio-api, multicam-api, menu-command-execution, api-coverage-matrix, localization-i18n, color-management, advanced-integration, production-case-studies, glossary, project-file-format, reverse-engineering-qe-dom

---

## Production Examples (16 files)

**ExtendScript (8):** batch-export-guarded, update-mogrt-text, cep-bridge-safe, qe-safe-wrapper, markers-batch-add, media-batch-relink, captions-batch-read, batch-import-organize, batch-effects-filters

**UXP (3):** list-sequences, batch-effects-captions, uxp-async-patterns

**CEP (2):** cep-theme-sync-panel.jsx, cep-theme-sync-panel.html

**UXP (3):** list-sequences, batch-effects-captions, uxp-async-patterns

**UXP Panel (1):** uxp-responsive-rubber-panel.html

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

**Complete Knowledge Base with 40 docs (36/40 complete, 90%), 16 production examples, comprehensive coverage of Premiere extensibility stack.**

**Last updated:** 2026-07-01  
**Tested on:** Premiere 25.6
