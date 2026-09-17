# Evidence review — 2026-09-17

## Confirmed from Adobe

UXP became generally available in Premiere 25.6. The inherited README grouped 25.0–25.6 together as GA; this was inaccurate. Use the [Adobe changelog](https://developer.adobe.com/premiere-pro/uxp/changelog/) and [Premiere API reference](https://developer.adobe.com/premiere-pro/uxp/ppro_reference/) for version-specific availability.

Adobe also documents [UXP hybrid plugins](https://blog.developer.adobe.com/en/publish/2026/04/uxp-hybrid-plugins-now-available-for-premiere). This is a relevant development surface beyond pure JavaScript UXP and deserves dedicated coverage.

## Claims requiring evidence

- The inherited README claimed complete coverage, production readiness and runtime testing on Premiere 25.6. Passing YAML checks and Python tests does not establish those claims. They have been removed from the main entry page.
- Specific CEP/ExtendScript retirement dates in historical documents are not validated by this audit. Check current Adobe host documentation before deciding compatibility or removal dates.
- `Sources/structured/knowledge/evidence/EVID-0002-runtime-observation-placeholder.yaml` assigns `experimentally_verified` confidence to an explicit placeholder. Treat it as unverified; the preserved source is retained byte-for-byte for traceability.
- UXP prototypes and caption automation approaches differ across source versions. None has been executed inside Premiere during this migration. Do not infer supported host methods from an example alone.

## What validation proves

SHA-256 validation proves preservation of imported bytes. The catalog groups only exact content duplicates. The 38-document frontmatter check proves metadata structure, and 17 Python tests cover the structured tools and Resolve fixtures. None of these checks proves exhaustive Adobe API coverage, runtime compatibility, or the truth of every imported statement.
