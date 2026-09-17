# Adobe Premiere development knowledge base

Consolidated reference material for Premiere plugins, extensions, automation and post-production workflows.

| Need | Entry point |
| --- | --- |
| Browse unique source contents | [Catalog](Consolidation/CATALOG.md) |
| Source collections and provenance | [Collection map](Consolidation/README.md) |
| Reliability and known inconsistencies | [Evidence review](Consolidation/EVIDENCE_REVIEW.md) |
| UXP, CEP, ExtendScript and SDK topics | [Knowledge](Knowledge/) |
| Host-specific examples | [Examples](Examples/) |
| Method contracts and interoperability | [Developer reference](developer_reference/) |
| YAML specifications, inventories and compiler | [Structured sources](Sources/structured/) |
| VFX tools and UXP prototypes | [VFX sources](Sources/vfx/) |
| Resolve adapter and fixtures | [Resolve sources](Sources/resolve/) |

The imported corpus contains 1,182 preserved files representing 612 distinct SHA-256 contents, alongside the existing GitHub reference layer. Preservation is complete for eligible files in the migration manifest; editorial integration and API verification are ongoing.

UXP general availability starts with Premiere 25.6. Check individual APIs against Adobe's [changelog](https://developer.adobe.com/premiere-pro/uxp/changelog/) and [API reference](https://developer.adobe.com/premiere-pro/uxp/ppro_reference/). Adobe also provides [hybrid UXP plugins](https://blog.developer.adobe.com/en/publish/2026/04/uxp-hybrid-plugins-now-available-for-premiere).

Historical lifecycle dates, confidence labels and production-readiness claims in preserved sources need separate verification. Python tests and metadata validation do not establish Premiere runtime compatibility.

## Validation

Install PyYAML and pytest in a Python 3.12 environment, then run:

```sh
python tools/validate_frontmatter.py
python tools/audit_corpus.py --check
(cd Sources/structured && python -m pytest -q)
(cd Sources/resolve && python -m pytest -q)
```

CI checks preservation, catalog consistency, metadata and Python tests. Add reviewed corrections to the reference layer with citations; preserved snapshots retain their original bytes.
