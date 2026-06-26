from dataclasses import dataclass, field
from typing import Any

@dataclass
class KnowledgeNode:
    id: str
    kind: str
    title: str
    path: str
    data: dict[str, Any]
    links: list[dict[str, str]] = field(default_factory=list)

@dataclass
class KnowledgeProject:
    name: str
    nodes: list[KnowledgeNode]
