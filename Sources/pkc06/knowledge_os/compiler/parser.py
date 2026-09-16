from pathlib import Path
import yaml
from knowledge_os.model import KnowledgeNode, KnowledgeProject

def load_project(source_dir: Path, name: str = "Premiere Pro Open AI Specification") -> KnowledgeProject:
    nodes = []
    for path in sorted(source_dir.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        kind = data.get("kind") or data.get("type") or "spec"
        node_id = data.get("id") or path.stem.upper()
        title = data.get("title") or data.get("name") or node_id
        links=[]
        for rel in ("owns","references","contains","uses","related","requires","prevents"):
            vals=data.get(rel,[]) or []
            if isinstance(vals,str): vals=[vals]
            for v in vals:
                links.append({"type":rel,"target":str(v)})
        nodes.append(KnowledgeNode(id=node_id, kind=kind, title=title, path=str(path), data=data, links=links))
    return KnowledgeProject(name=name, nodes=nodes)
