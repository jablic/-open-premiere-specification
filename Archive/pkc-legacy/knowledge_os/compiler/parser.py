from pathlib import Path
import yaml
from knowledge_os.model import KnowledgeNode, KnowledgeProject

LINK_FIELDS = (
    'owns', 'references', 'contains', 'uses', 'related', 'requires', 'prevents',
    'depends_on', 'implements', 'validates', 'covers', 'ownership'
)

def _link_values(key, value):
    if not value:
        return []
    if key == 'ownership' and isinstance(value, dict):
        vals=[]
        for subkey in ('owner', 'children', 'owns', 'references'):
            v=value.get(subkey)
            if isinstance(v, list): vals.extend(v)
            elif v: vals.append(v)
        return vals
    if isinstance(value, list): return value
    if isinstance(value, dict): return list(value.values())
    return [value]

def load_project(source_dir: Path, name: str = 'Premiere Pro Open AI Specification') -> KnowledgeProject:
    nodes = []
    for path in sorted(source_dir.rglob('*.yaml')):
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        kind = data.get('kind') or data.get('type') or 'spec'
        node_id = data.get('id') or path.stem.upper()
        title = data.get('title') or data.get('name') or node_id
        links=[]
        for rel in LINK_FIELDS:
            for v in _link_values(rel, data.get(rel)):
                if isinstance(v, list):
                    for vv in v: links.append({'type':rel,'target':str(vv)})
                else:
                    links.append({'type':rel,'target':str(v)})
        nodes.append(KnowledgeNode(id=node_id, kind=kind, title=title, path=str(path), data=data, links=links))
    return KnowledgeProject(name=name, nodes=nodes)
