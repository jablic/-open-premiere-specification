"""Read-only boundary. No Resolve mutation methods are exposed here."""
import hashlib, json
from vfx_core.models import CompleteResult, DiagnosticsReport, MarkerRef, ProjectSnapshot, TimelineSnapshot
class ResolveReadOnlyAdapter:
    def __init__(self, api, api_version="unknown"): self.api=api; self.api_version=api_version; self.source="resolve_api"
    def _result(self,value):
        sid=hashlib.sha256(json.dumps(value,default=str,sort_keys=True).encode()).hexdigest()[:16]
        return CompleteResult("ok",value,source=self.source,api_version=self.api_version,snapshot_id=sid)
    def get_active_project(self):
        data = self.api.get_project()
        return self._result(ProjectSnapshot(str(data.get("id", "")), str(data.get("name", ""))))
    def get_active_timeline(self): return self._result(TimelineSnapshot(**self.api.get_timeline()))
    def get_markers(self,timeline=None):
        data=self.api.get_markers(timeline)
        if not isinstance(data,dict) or not data.get("complete",False): return CompleteResult("incomplete",warnings=("Marker enumeration is incomplete; no write operation may proceed.",),source=self.source,api_version=self.api_version,complete=False)
        return self._result([MarkerRef(**x) for x in data["items"]])
    def get_timeline_items(self,timeline=None,track_filter=None):
        data=self.api.get_timeline_items(timeline,track_filter)
        if not isinstance(data,dict) or not data.get("complete",False): return CompleteResult("incomplete",errors=("Timeline item enumeration is incomplete.",),source=self.source,api_version=self.api_version,complete=False)
        return self._result(data["items"])

    def diagnostics(self):
        checks=[]; warnings=[]; errors=[]
        project=self.get_active_project(); timeline=self.get_active_timeline()
        if project.status == "ok" and project.value.project_name: checks.append("active_project")
        else: errors.append("active project unavailable")
        if timeline.status == "ok" and timeline.value.duration_frames > 0: checks.append("active_timeline")
        else: errors.append("active timeline unavailable or empty")
        required=("Workflow Integration bridge availability/version", "Resolve payload shape", "enumeration completeness", "exact FPS semantics", "displayed TC/frame conversion")
        return DiagnosticsReport("ok" if not errors else "error", tuple(checks), tuple(warnings), tuple(errors), required)
