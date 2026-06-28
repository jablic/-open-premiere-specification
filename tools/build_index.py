#!/usr/bin/env python3
"""Build query index and RAG chunks from Knowledge/*.md frontmatter."""
from __future__ import annotations

import json
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
BUILD = ROOT / "build"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    end = text.find("\n---", 3)
    fm = yaml.safe_load(text[3:end].strip())
    body = text[end + 4 :].lstrip("\n")
    return fm, body


def split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "_preamble"
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^(#{2,3})\s+(.+)$", line)
        if m:
            sections[current] = "\n".join(buf).strip()
            buf = []
            slug = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            current = slug
        else:
            buf.append(line)
    sections[current] = "\n".join(buf).strip()
    return {k: v for k, v in sections.items() if v}


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    index: list[dict] = []
    chunks: list[dict] = []

    for path in sorted(KNOWLEDGE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        doc_id = fm["id"]
        sections = split_sections(body)

        entry = {
            "id": doc_id,
            "title": fm["title"],
            "category": fm["category"],
            "status": fm["status"],
            "doc_status": fm["doc_status"],
            "tags": fm.get("tags", []),
            "related": fm.get("related", []),
            "api_namespace": fm.get("api_namespace"),
            "min_premiere_version": fm.get("min_premiere_version"),
            "path": f"Knowledge/{path.name}",
        }
        index.append(entry)

        for section, content in sections.items():
            chunks.append({
                "doc_id": doc_id,
                "title": fm["title"],
                "section": section,
                "status": fm["status"],
                "tags": fm.get("tags", []),
                "text": content,
                "source": f"Knowledge/{path.name}#{section}",
            })

    (BUILD / "query_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    with (BUILD / "rag_chunks.jsonl").open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    complete = sum(1 for e in index if e["doc_status"] == "complete")
    report = (
        f"# Knowledge Base Status\n\n"
        f"- Documents: {len(index)}\n"
        f"- Complete: {complete}\n"
        f"- Partial: {sum(1 for e in index if e['doc_status'] == 'partial')}\n"
        f"- RAG chunks: {len(chunks)}\n"
    )
    (BUILD / "status_report.md").write_text(report, encoding="utf-8")
    print(f"Built index: {len(index)} docs, {len(chunks)} chunks → build/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
