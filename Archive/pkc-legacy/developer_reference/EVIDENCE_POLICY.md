# Evidence Policy

The Developer Reference is evidence-based. Every non-trivial technical claim must be traceable to a source category.

## Evidence levels

### A — Official Adobe

Official Adobe documentation, Adobe Developer pages, SDK headers, SDK documentation, or official Adobe repositories.

### B — Adobe Sample

Official Adobe sample projects, such as PProPanel or UXP sample panels.

### C — Reproduced Experiment

A result reproduced in a controlled Premiere Pro environment and documented in this repository.

### D — Community Verified

A result independently confirmed by multiple developers, forum posts, issues, or community documents.

### E — Hypothesis

A plausible but unverified statement. Hypotheses MUST NOT be written as facts.

## Required evidence by section

- Official API signature: A or B.
- QE DOM behaviour: C or D minimum; A only if Adobe explicitly documents it.
- Production workflow recommendation: C or production observation.
- Known bug: C, D, or linked public issue.
- Version compatibility: A or C.

## Evidence notation

Use this pattern in reference pages:

```text
Evidence: A-UXP-001, B-PPROPANEL-001, C-EXP-0007
```

## Prohibited patterns

- Citing AI-generated text as evidence.
- Treating a single forum post as verified fact.
- Treating QE observations from one Premiere version as universal.
- Treating generated documentation as a primary source.
