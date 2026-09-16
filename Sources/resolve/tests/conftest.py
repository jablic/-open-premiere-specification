import json
from pathlib import Path
import pytest
@pytest.fixture
def fixture_dir():
    return Path(__file__).parent / "fixtures" / "resolve"

@pytest.fixture
def fixture_api():
    class API:
        def __init__(self): self.data=json.loads((Path(__file__).parent/"fixtures/resolve/active_timeline_24fps_start_01h.json").read_text())
        def get_project(self): return {"name":"Fixture Project"}
        def get_timeline(self): return self.data["timeline"]
        def get_markers(self,_): return {"complete":True,"items":self.data["markers"]}
        def get_timeline_items(self,_,__): return {"complete":True,"items":self.data["items"]}
    return API()
