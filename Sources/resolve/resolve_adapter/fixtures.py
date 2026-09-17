import json
from pathlib import Path

def load_fixture(path: str | Path) -> dict:
    """Load a captured/synthetic fixture; never contacts Resolve."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
