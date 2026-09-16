from dataclasses import dataclass
from typing import Generic, Optional, TypeVar
T = TypeVar("T")
@dataclass(frozen=True)
class ProjectSnapshot:
    project_id: str
    project_name: str
@dataclass(frozen=True)
class CompleteResult(Generic[T]):
    status: str
    value: Optional[T] = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    source: str = "unknown"
    api_version: str = "unknown"
    snapshot_id: str = ""
    complete: bool = True
@dataclass(frozen=True)
class TimelineSnapshot:
    sequence_id: str; sequence_name: str; fps_exact: float; nominal_fps: int; drop_frame: bool
    timeline_start_frame: int; timeline_start_timecode: str; duration_frames: int
    width: int; height: int; snapshot_id: str
@dataclass(frozen=True)
class DiagnosticsReport:
    status: str
    checks: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    live_verification_required: tuple[str, ...] = ()
@dataclass(frozen=True)
class MarkerRef:
    id: str; name: str; comments: str; frame: int; duration_frames: int = 1; color: str = ""
@dataclass(frozen=True)
class ShotRef:
    id: str; source: str; start_frame: int; end_frame_exclusive: int; duration_frames: int
    track: Optional[int] = None; source_path: Optional[str] = None; source_in_frame: Optional[int] = None
    source_out_frame: Optional[int] = None; fps: Optional[float] = None; sequence_id: str = ""
    @property
    def out_frame_inclusive(self): return self.end_frame_exclusive - 1
