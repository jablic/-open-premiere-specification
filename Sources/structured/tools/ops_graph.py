#!/usr/bin/env python3
"""OPS Knowledge Graph Engine v0.1.

Builds a machine-readable graph from OPS knowledge cards in knowledge/**/*.yaml.
Outputs:
  build/graph/knowledge_graph.json
  build/graph/knowledge_graph.mmd
  build/graph/knowledge_graph.dot
  build/graph/graph_report.md

This module is intentionally standalone: it does not require changes to the
existing PKC compiler and can be called independently or from CI.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    yaml = None

ROOT = Path.cwd()
DEFAULT_KNOWLEDGE_DIR = ROOT / "knowledge"
DEFAULT_OUT_DIR = ROOT / "build" / "graph"

RELATION_FIELDS = {
    "owns": "owns",
    "owned_by": "owned_by",
    "contains": "contains",
    "references": "references",
    "serializes": "serializes",
    "serialization": "serializes",
    "api": "uses_api",
    "rules": "constrained_by",
    "tests": "tested_by",
    "recipes": "implemented_by_recipe",
    "capabilities": "supports_capability",
    "evidence": "supported_by_evidence",
    "experiments": "supported_by_experiment",
    "known_bugs": "affected_by_bug",
    "bugs": "affected_by_bug",
}

KIND_DIR_MAP = {
    "objects": "object",
    "rules": "rule",
    "tests": "test",
    "evidence": "evidence",
    "capabilities": "capability",
    "recipes": "recipe",
    "api": "api",
    "serialization": "serialization",
    "experiments": "experiment",
    "bugs": "bug",
    "constraints": "constraint",
    "relations": "relation",
}

ID_RE = re.compile(r"^[A-Z]+-[0-9]{4,}$")

@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    name: str
    path: str
    summary: str = ""
    status: str = "unknown"

@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    relation: str
    source_path: str
    evidence: List[str]
    confidence: str = "unknown"


def load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with: pip3 install pyyaml")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def infer_kind(path: Path, data: Dict[str, Any], knowledge_dir: Path) -> str:
    explicit = data.get("kind") or data.get("type")
    if explicit:
        return str(explicit).lower()
    try:
        first = path.relative_to(knowledge_dir).parts[0]
        return KIND_DIR_MAP.get(first, first.rstrip("s"))
    except Exception:
        return "unknown"


def normalize_items(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, list):
        result: List[str] = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Supports forms like {id: OBJ-0001} or {target: OBJ-0001}
                for key in ("id", "target", "name", "object"):
                    if key in item:
                        result.append(str(item[key]))
                        break
            else:
                result.append(str(item))
        return result
    if isinstance(value, dict):
        # Supports nested maps such as api: {extendscript: true, uxp: partial}
        return [str(k) for k, v in value.items() if v not in (False, None, "false", "none")]
    return [str(value)]


def card_id(data: Dict[str, Any], path: Path) -> str:
    cid = data.get("id") or data.get("uid")
    if cid:
        return str(cid)
    return path.stem.upper().replace("_", "-")


def card_name(data: Dict[str, Any], fallback_id: str) -> str:
    return str(data.get("name") or data.get("title") or fallback_id)


def card_summary(data: Dict[str, Any]) -> str:
    s = data.get("summary") or data.get("description") or ""
    if isinstance(s, dict):
        return json.dumps(s, ensure_ascii=False)
    return str(s).strip()


def card_status(data: Dict[str, Any]) -> str:
    return str(data.get("status") or "unknown")


def discover_cards(knowledge_dir: Path) -> Tuple[Dict[str, Node], Dict[str, Dict[str, Any]], List[str]]:
    nodes: Dict[str, Node] = {}
    raw: Dict[str, Dict[str, Any]] = {}
    warnings: List[str] = []
    if not knowledge_dir.exists():
        return nodes, raw, [f"Knowledge directory not found: {knowledge_dir}"]
    for path in sorted(knowledge_dir.rglob("*.yaml")):
        try:
            data = load_yaml(path)
        except Exception as exc:
            warnings.append(f"Failed to read {path}: {exc}")
            continue
        cid = card_id(data, path)
        kind = infer_kind(path, data, knowledge_dir)
        node = Node(
            id=cid,
            kind=kind,
            name=card_name(data, cid),
            path=str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
            summary=card_summary(data),
            status=card_status(data),
        )
        if cid in nodes:
            warnings.append(f"Duplicate node id {cid}: {nodes[cid].path} and {node.path}")
        nodes[cid] = node
        raw[cid] = data
    return nodes, raw, warnings


def resolve_target(value: str, nodes: Dict[str, Node]) -> str:
    # Prefer exact ID. If user wrote object name, resolve by node.name.
    if value in nodes:
        return value
    normalized = value.strip().lower()
    matches = [nid for nid, node in nodes.items() if node.name.lower() == normalized]
    if len(matches) == 1:
        return matches[0]
    return value


def collect_edges(nodes: Dict[str, Node], raw: Dict[str, Dict[str, Any]]) -> List[Edge]:
    edges: List[Edge] = []
    for source_id, data in raw.items():
        source_path = nodes[source_id].path
        evidence = normalize_items(data.get("evidence"))
        confidence = str(data.get("confidence") or data.get("quality", {}).get("confidence") if isinstance(data.get("quality"), dict) else "unknown")
        for field, relation in RELATION_FIELDS.items():
            if field not in data:
                continue
            for target_value in normalize_items(data.get(field)):
                target_id = resolve_target(target_value, nodes)
                if target_id == source_id:
                    continue
                edges.append(Edge(source_id, target_id, relation, source_path, evidence, confidence))
        # Supports nested ownership: ownership: {owns: [...], references: [...]}
        ownership = data.get("ownership")
        if isinstance(ownership, dict):
            for nested_field in ("owns", "owned_by", "contains", "references"):
                if nested_field in ownership:
                    rel = RELATION_FIELDS.get(nested_field, nested_field)
                    for target_value in normalize_items(ownership.get(nested_field)):
                        target_id = resolve_target(target_value, nodes)
                        if target_id != source_id:
                            edges.append(Edge(source_id, target_id, rel, source_path, evidence, confidence))
    # De-duplicate while preserving order.
    seen = set()
    unique: List[Edge] = []
    for e in edges:
        key = (e.source, e.target, e.relation)
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def build_graph(knowledge_dir: Path = DEFAULT_KNOWLEDGE_DIR) -> Dict[str, Any]:
    nodes, raw, warnings = discover_cards(knowledge_dir)
    edges = collect_edges(nodes, raw)
    missing_targets = sorted({e.target for e in edges if e.target not in nodes})
    graph = {
        "schema": "ops.knowledge_graph.v1",
        "generated_by": "tools/ops_graph.py",
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "missing_targets": len(missing_targets),
            "warnings": len(warnings),
        },
        "nodes": [asdict(n) for n in sorted(nodes.values(), key=lambda n: n.id)],
        "edges": [asdict(e) for e in edges],
        "missing_targets": missing_targets,
        "warnings": warnings,
    }
    return graph


def safe_node_id(identifier: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", identifier)


def write_mermaid(graph: Dict[str, Any], path: Path) -> None:
    lines = ["graph TD"]
    nodes = {n["id"]: n for n in graph["nodes"]}
    for n in graph["nodes"]:
        sid = safe_node_id(n["id"])
        label = f'{n["id"]}<br/>{n["name"]}'
        lines.append(f'  {sid}["{label}"]')
    for e in graph["edges"]:
        src = safe_node_id(e["source"])
        dst = safe_node_id(e["target"])
        label = e["relation"]
        lines.append(f"  {src} -- {label} --> {dst}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dot(graph: Dict[str, Any], path: Path) -> None:
    lines = ["digraph OPSKnowledgeGraph {", "  rankdir=LR;", "  node [shape=box];"]
    for n in graph["nodes"]:
        sid = safe_node_id(n["id"])
        label = f'{n["id"]}\\n{n["name"]}'
        lines.append(f'  {sid} [label="{label}"];')
    for e in graph["edges"]:
        lines.append(f'  {safe_node_id(e["source"])} -> {safe_node_id(e["target"])} [label="{e["relation"]}"];')
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(graph: Dict[str, Any], path: Path) -> None:
    by_kind: Dict[str, int] = {}
    by_relation: Dict[str, int] = {}
    for n in graph["nodes"]:
        by_kind[n["kind"]] = by_kind.get(n["kind"], 0) + 1
    for e in graph["edges"]:
        by_relation[e["relation"]] = by_relation.get(e["relation"], 0) + 1
    lines = [
        "# OPS Knowledge Graph Report",
        "",
        f"Nodes: **{graph['stats']['nodes']}**",
        f"Edges: **{graph['stats']['edges']}**",
        f"Missing targets: **{graph['stats']['missing_targets']}**",
        "",
        "## Nodes by Kind",
        "",
    ]
    for k, v in sorted(by_kind.items()):
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Edges by Relation", ""]
    for k, v in sorted(by_relation.items()):
        lines.append(f"- `{k}`: {v}")
    if graph["missing_targets"]:
        lines += ["", "## Missing Targets", ""]
        for target in graph["missing_targets"]:
            lines.append(f"- `{target}`")
    if graph["warnings"]:
        lines += ["", "## Warnings", ""]
        for warning in graph["warnings"]:
            lines.append(f"- {warning}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(graph: Dict[str, Any], out_dir: Path = DEFAULT_OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "knowledge_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    write_mermaid(graph, out_dir / "knowledge_graph.mmd")
    write_dot(graph, out_dir / "knowledge_graph.dot")
    write_report(graph, out_dir / "graph_report.md")


def validate_graph(graph: Dict[str, Any]) -> int:
    errors: List[str] = []
    node_ids = {n["id"] for n in graph["nodes"]}
    for e in graph["edges"]:
        if e["source"] not in node_ids:
            errors.append(f"Missing source: {e['source']} in edge {e}")
        if e["target"] not in node_ids and ID_RE.match(str(e["target"])):
            errors.append(f"Missing target: {e['target']} referenced by {e['source']} via {e['relation']}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print("OK: graph validation passed.")
    return 0


def query_graph(graph: Dict[str, Any], term: str) -> int:
    term_l = term.lower()
    nodes = {n["id"]: n for n in graph["nodes"]}
    matched = [n for n in graph["nodes"] if term_l in n["id"].lower() or term_l in n["name"].lower()]
    if not matched:
        print(f"No nodes matched: {term}")
        return 1
    for node in matched:
        print(f"\n{node['id']} — {node['name']} ({node['kind']})")
        print(f"  path: {node['path']}")
        outgoing = [e for e in graph["edges"] if e["source"] == node["id"]]
        incoming = [e for e in graph["edges"] if e["target"] == node["id"]]
        if outgoing:
            print("  outgoing:")
            for e in outgoing:
                target = nodes.get(e["target"], {"name": e["target"]})
                print(f"    - {e['relation']} -> {e['target']} ({target['name']})")
        if incoming:
            print("  incoming:")
            for e in incoming:
                source = nodes.get(e["source"], {"name": e["source"]})
                print(f"    - {e['source']} ({source['name']}) -> {e['relation']}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="OPS Knowledge Graph Engine")
    sub = parser.add_subparsers(dest="command", required=True)
    p_build = sub.add_parser("build")
    p_build.add_argument("--knowledge", default=str(DEFAULT_KNOWLEDGE_DIR))
    p_build.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--knowledge", default=str(DEFAULT_KNOWLEDGE_DIR))
    p_query = sub.add_parser("query")
    p_query.add_argument("term")
    p_query.add_argument("--knowledge", default=str(DEFAULT_KNOWLEDGE_DIR))
    args = parser.parse_args(argv)

    graph = build_graph(Path(args.knowledge))
    if args.command == "build":
        write_outputs(graph, Path(args.out))
        print(f"Built graph: {graph['stats']['nodes']} nodes, {graph['stats']['edges']} edges")
        print(f"Output: {Path(args.out)}")
        return 0
    if args.command == "validate":
        return validate_graph(graph)
    if args.command == "query":
        return query_graph(graph, args.term)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
