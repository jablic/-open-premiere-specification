from dataclasses import dataclass

@dataclass(frozen=True)
class ExportConfig:
    shot_id_column: str = "Shot ID"
    include_source_metadata: bool = True
    output_format: str = "csv"
    overwrite: bool = False

    def __post_init__(self):
        if self.output_format.lower() not in {"csv", "txt", "html", "xlsx", "pdf"}:
            raise ValueError("unsupported export format")

@dataclass(frozen=True)
class ColumnSpec:
    key: str
    label: str
    enabled: bool = True

DEFAULT_COLUMNS = (
    ColumnSpec("id", "Shot ID"), ColumnSpec("tc_in", "TC IN"),
    ColumnSpec("tc_out", "TC OUT"), ColumnSpec("duration_frames", "Duration (frames)"),
)
