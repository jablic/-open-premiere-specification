from resolve_adapter.fixtures import load_fixture
from resolve_adapter import ResolveReadOnlyAdapter

def test_all_resolve_fixture_timelines_have_required_contract(fixture_dir):
    names = ["active_timeline_24fps_start_01h.json", "active_timeline_24fps_start_03h.json", "active_timeline_23_976_non_drop.json", "active_timeline_mixed_tracks_markers.json"]
    for name in names:
        data = load_fixture(fixture_dir / name)
        timeline = data["timeline"]
        assert {"sequence_id", "fps_exact", "nominal_fps", "timeline_start_frame", "duration_frames"} <= timeline.keys()
        assert timeline["duration_frames"] > 0

def test_diagnostics_is_read_only_and_labels_live_gaps(fixture_api):
    result = ResolveReadOnlyAdapter(fixture_api, "fixture").diagnostics()
    assert result.status == "ok"
    assert "active_timeline" in result.checks
    assert result.live_verification_required
