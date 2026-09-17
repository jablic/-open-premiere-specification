# Consolidated Premiere development corpus

This repository combines the GitHub main knowledge base with the complete eligible local source collections recovered on 2026-09-17. The original root Knowledge, Examples and developer_reference directories remain the published reference layer.

## Collections

| Directory | Contents |
| --- | --- |
| [Structured](../Sources/structured/) | YAML specifications, evidence, API inventories, compiler, generated reference documents, tests and Text AI Agent prototype |
| [VFX](../Sources/vfx/) | VFX tools, UXP prototypes, local uncommitted documentation and NLE research |
| [v2](../Sources/v2/) | Markdown-first reference variant and historical compiler |
| [PKC 0.7](../Sources/pkc07/) | Standalone compiler version |
| [PKC 0.6](../Sources/pkc06/) | Historical compiler source |
| [Builder](../Sources/builder/) | PPAIKB builder |
| [Resolve](../Sources/resolve/) | Resolve adapter, fixtures and VFX models |
| [Imports](../Sources/imports/) | Original import variants |
| [Drafts](../Sources/drafts/) | Unreviewed imported notes |

`manifest.json` records every inventoried file with its source, size, SHA-256, destination or exclusion reason. Included files are byte-identical to their local originals. Binary installers, Git internals, caches, machine-specific agent settings and build outputs remain in local backups and are not published as source.

## Evidence and limitations

Preservation does not establish technical accuracy. Historical documents can disagree about API support, product versions, or implementation viability. Sources are preserved separately so neither an older claim nor an untested prototype silently overrides current reference material. In particular, imported frontmatter confidence labels have not been independently revalidated against Adobe documentation or a running Premiere host.

The collection is complete for eligible source files in the inventoried local sets, not a claim of exhaustive Adobe API coverage. Deduplicated editorial integration and runtime validation remain separate work.

## Local validation

From the workspace root:

```sh
(cd Premiere_Consolidated && ../_tools/venv/bin/python tools/validate_frontmatter.py)
(cd Premiere_Consolidated/Sources/structured && ../../../_tools/venv/bin/python -m pytest -q)
(cd Premiere_Consolidated/Sources/resolve && ../../../_tools/venv/bin/python -m pytest -q)
```
