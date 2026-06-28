from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ops_coverage import build_report, validate_coverage  # noqa: E402


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_coverage_reports_counts_and_readiness():
    with tempfile.TemporaryDirectory() as td:
        k = Path(td) / "knowledge"
        write(k / "objects" / "OBJ-0001-application.yaml", """
id: OBJ-0001
kind: object
name: Application
tests:
  - TEST-0001
evidence:
  - EVID-0001
""")
        write(k / "tests" / "TEST-0001-application.yaml", """
id: TEST-0001
kind: test
name: Application test
""")
        write(k / "evidence" / "EVID-0001-source.yaml", """
id: EVID-0001
kind: evidence
name: Evidence source
""")
        report = build_report(k)
        assert report["summary"]["nodes"] == 3
        assert report["summary"]["edges"] == 2
        assert report["summary"]["errors"] == 0
        assert report["readiness"]["OBJ-0001"]["score"] == 100
        assert validate_coverage(report) == 0


def test_coverage_fails_on_missing_graph_targets():
    with tempfile.TemporaryDirectory() as td:
        k = Path(td) / "knowledge"
        write(k / "objects" / "OBJ-0001-application.yaml", """
id: OBJ-0001
kind: object
name: Application
tests:
  - TEST-9999
""")
        report = build_report(k)
        assert report["summary"]["errors"] == 1
        assert validate_coverage(report) == 1
