from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ops_graph import build_graph, validate_graph  # noqa: E402


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_graph_builds_edges_from_object_cards():
    with tempfile.TemporaryDirectory() as td:
        k = Path(td) / "knowledge"
        write(k / "objects" / "OBJ-0001-application.yaml", """
id: OBJ-0001
kind: object
name: Application
owns:
  - OBJ-0002
rules:
  - RULE-0001
""")
        write(k / "objects" / "OBJ-0002-project.yaml", """
id: OBJ-0002
kind: object
name: Project
references:
  - OBJ-0001
""")
        write(k / "rules" / "RULE-0001-no-fake-api.yaml", """
id: RULE-0001
kind: rule
name: No fake API
""")
        graph = build_graph(k)
        edges = {(e["source"], e["relation"], e["target"]) for e in graph["edges"]}
        assert ("OBJ-0001", "owns", "OBJ-0002") in edges
        assert ("OBJ-0001", "constrained_by", "RULE-0001") in edges
        assert ("OBJ-0002", "references", "OBJ-0001") in edges
        assert graph["stats"]["nodes"] == 3


def test_graph_validation_accepts_resolved_ids():
    with tempfile.TemporaryDirectory() as td:
        k = Path(td) / "knowledge"
        write(k / "objects" / "OBJ-0001-a.yaml", """
id: OBJ-0001
kind: object
name: A
owns:
  - OBJ-0002
""")
        write(k / "objects" / "OBJ-0002-b.yaml", """
id: OBJ-0002
kind: object
name: B
""")
        graph = build_graph(k)
        assert validate_graph(graph) == 0
