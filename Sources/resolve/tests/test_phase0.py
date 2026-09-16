from vfx_core.timecode import FrameRate, Timecode
from vfx_core.shot_model import shots_from_markers
from resolve_adapter import ResolveReadOnlyAdapter
def test_timecode_roundtrip():
    for rate, values in [(FrameRate(24),["01:00:00:00","03:00:00:00"]),(FrameRate(30000/1001,True),["01:00:00:00","01:00:59:29"]),(FrameRate(24000/1001),["00:00:00:00"] )]:
        for value in values: assert Timecode.parse(value,rate).format()==value
def test_active_timeline_contract(fixture_api):
    a=ResolveReadOnlyAdapter(fixture_api,"fixture"); t=a.get_active_timeline().value
    shots=shots_from_markers(t,a.get_markers(t).value)
    assert t.timeline_start_frame==86400 and [s.id for s in shots]==["SH010","SH020"]
    assert shots[0].out_frame_inclusive==shots[0].start_frame+47
def test_incomplete_enumeration_blocks(fixture_api):
    fixture_api.get_markers=lambda _: {"complete":False,"items":[]}
    r=ResolveReadOnlyAdapter(fixture_api).get_markers(); assert r.status=="incomplete" and not r.complete
