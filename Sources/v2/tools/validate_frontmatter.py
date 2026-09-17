#!/usr/bin/env python3
"""Validate Knowledge/*.md frontmatter and cross-references."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "Knowledge"

REQUIRED = {
    "id", "title", "category", "status", "doc_status", "tags", "related",
    "sources", "last_verified", "verified_against_version",
}
VALID_STATUS = {"current", "legacy", "deprecated", "undocumented", "mixed"}
VALID_DOC_STATUS = {"complete", "partial", "stub"}
VALID_CATEGORY = {
    "scripting", "ui-extensibility", "native", "interop", "data-format",
    "workflow", "meta",
}


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---"):
        return None, "missing opening ---"
    end = text.find("\n---", 3)
    if end == -1:
        return None, "missing closing ---"
    block = text[3:end].strip()
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return data, ""


def main() -> int:
    errors: list[str] = []
    ids: dict[str, str] = {}

    for path in sorted(KNOWLEDGE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, err = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{path.name}: {err}")
            continue

        doc_id = fm.get("id")
        if not doc_id:
            errors.append(f"{path.name}: missing id")
            continue
        if doc_id in ids:
            errors.append(f"{path.name}: duplicate id '{doc_id}' (also in {ids[doc_id]})")
        else:
            ids[doc_id] = path.name

        expected = path.stem
        if doc_id != expected and not expected.startswith("00-"):
            errors.append(f"{path.name}: id '{doc_id}' != filename stem '{expected}'")

        missing = REQUIRED - set(fm.keys())
        if missing:
            errors.append(f"{path.name}: missing fields: {sorted(missing)}")

        if fm.get("status") not in VALID_STATUS:
            errors.append(f"{path.name}: invalid status '{fm.get('status')}'")
        if fm.get("doc_status") not in VALID_DOC_STATUS:
            errors.append(f"{path.name}: invalid doc_status '{fm.get('doc_status')}'")
        if fm.get("category") not in VALID_CATEGORY:
            errors.append(f"{path.name}: invalid category '{fm.get('category')}'")

        if fm.get("doc_status") == "stub":
            errors.append(f"{path.name}: doc_status is still 'stub'")

    for path in sorted(KNOWLEDGE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if not fm:
            continue
        for rel in fm.get("related") or []:
            if rel not in ids:
                errors.append(f"{path.name}: related id '{rel}' not found")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    complete = sum(
        1 for p in KNOWLEDGE.glob("*.md")
        if (parse_frontmatter(p.read_text(encoding="utf-8"))[0] or {}).get("doc_status") == "complete"
    )
    total = len(list(KNOWLEDGE.glob("*.md")))
    print(f"OK: {total} Knowledge docs validated ({complete} complete, 0 stubs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
