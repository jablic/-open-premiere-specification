from vfx_core import ExportConfig, collision_safe_path, manifest_json
from vfx_core.shot_model import shots_from_markers
from resolve_adapter import ResolveReadOnlyAdapter

def test_config_and_collision_are_pure(fixture_api, tmp_path):
    assert ExportConfig(output_format="XLSX").output_format == "XLSX"
    assert collision_safe_path(tmp_path, "SH010", "mov", existing=[tmp_path / "SH010.mov"]).name == "SH010_2.mov"

def test_manifest_preserves_exclusive_range(fixture_api):
    adapter = ResolveReadOnlyAdapter(fixture_api)
    timeline = adapter.get_active_timeline().value
    shots = shots_from_markers(timeline, adapter.get_markers(timeline).value)
    manifest = manifest_json(timeline, shots)
    assert '"end_frame_exclusive": 86448' in manifest
    assert '"schema": "vfx-shot-manifest/1"' in manifest
