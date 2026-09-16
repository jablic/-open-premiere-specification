import json
from dataclasses import asdict
from .models import ShotRef, TimelineSnapshot

def shot_manifest(snapshot: TimelineSnapshot, shots: list[ShotRef]) -> dict:
    return {"schema": "vfx-shot-manifest/1", "snapshot": asdict(snapshot), "shots": [asdict(s) for s in shots]}

def manifest_json(snapshot: TimelineSnapshot, shots: list[ShotRef]) -> str:
    return json.dumps(shot_manifest(snapshot, shots), ensure_ascii=False, indent=2, sort_keys=True)
