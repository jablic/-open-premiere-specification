from .models import MarkerRef, ShotRef, TimelineSnapshot
def shots_from_markers(snapshot: TimelineSnapshot, markers: list[MarkerRef]):
    out=[]; seen=set()
    for marker in sorted(markers,key=lambda x:x.frame):
        sid=(marker.name or marker.comments).strip()
        if not sid: continue
        if sid in seen: raise ValueError(f"duplicate shot id: {sid}")
        seen.add(sid); start=marker.frame; end=start+max(1,marker.duration_frames)
        if start < snapshot.timeline_start_frame or end > snapshot.timeline_start_frame+snapshot.duration_frames: raise ValueError(f"shot range outside timeline: {sid}")
        out.append(ShotRef(sid,"timeline_marker",start,end,end-start,sequence_id=snapshot.sequence_id))
    return out
