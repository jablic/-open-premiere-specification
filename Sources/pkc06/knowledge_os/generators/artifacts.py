from pathlib import Path
import json


def write_artifacts(project, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    ast = {
        "project": project.name,
        "nodes": [
            {"id": n.id, "kind": n.kind, "title": n.title, "data": n.data, "links": n.links}
            for n in project.nodes
        ],
    }
    (out_dir / "knowledge_ast.json").write_text(json.dumps(ast, ensure_ascii=False, indent=2), encoding="utf-8")
    graph = {
        "nodes": [{"id": n.id, "label": n.title, "kind": n.kind} for n in project.nodes],
        "edges": [],
    }
    for n in project.nodes:
        for l in n.links:
            graph["edges"].append({"source": n.id, "target": l["target"], "type": l["type"]})
    (out_dir / "knowledge_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    rulepack = [
        {
            "id": n.id,
            "title": n.title,
            "severity": n.data.get("severity", "info"),
            "rule": n.data.get("rule") or n.data.get("summary"),
        }
        for n in project.nodes
        if n.kind == "rule"
    ]
    (out_dir / "ai_rulepack.json").write_text(json.dumps(rulepack, ensure_ascii=False, indent=2), encoding="utf-8")
    digital = {"objects": [n.data for n in project.nodes if n.kind == "object"]}
    (out_dir / "digital_twin.json").write_text(json.dumps(digital, ensure_ascii=False, indent=2), encoding="utf-8")
    tests = [n.data for n in project.nodes if n.kind in ("test", "benchmark", "evaluation")]
    (out_dir / "test_manifest.json").write_text(json.dumps(tests, ensure_ascii=False, indent=2), encoding="utf-8")


def write_rag(markdown_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    fp = out_dir / "rag_chunks.jsonl"
    with fp.open("w", encoding="utf-8") as f:
        for p in sorted(markdown_dir.rglob("*.md")):
            text = p.read_text(encoding="utf-8")
            paras = [x.strip() for x in text.split("\n\n") if x.strip()]
            for i, para in enumerate(paras):
                f.write(json.dumps({"source": p.relative_to(markdown_dir).as_posix(), "chunk": i, "text": para}, ensure_ascii=False) + "\n")
