from knowledge_os.model import KnowledgeProject

REQUIRED = {"object": ["id", "kind", "title"], "rule": ["id", "kind", "title"], "serialization": ["id", "kind", "title"]}

def validate_project(project: KnowledgeProject) -> list[str]:
    errors=[]
    seen={}
    for n in project.nodes:
        if n.id in seen:
            errors.append(f"Duplicate id {n.id}: {n.path} and {seen[n.id]}")
        seen[n.id]=n.path
        for field in REQUIRED.get(n.kind, ["id","kind","title"]):
            if field not in n.data:
                errors.append(f"{n.id}: missing required field: {field}")
        if n.kind == "object" and "ownership" in n.data:
            own=n.data.get("ownership") or {}
            if "owns" in own and isinstance(own["owns"], str):
                errors.append(f"{n.id}: ownership.owns must be a list")
    return errors
