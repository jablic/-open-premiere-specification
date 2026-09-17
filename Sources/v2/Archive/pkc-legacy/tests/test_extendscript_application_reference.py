from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]


def test_application_reference_exists_and_has_required_sections():
    path = ROOT / "developer_reference" / "extendscript" / "Application" / "README.md"
    assert path.exists(), "Application reference chapter is missing"
    text = path.read_text(encoding="utf-8")
    required = [
        "# ExtendScript Application Reference",
        "## 1. Purpose",
        "## 6. Attribute index",
        "## 7. Method index",
        "## 8. Developer contracts",
        "## 9. Failure modes to document experimentally",
        "## 10. Production guidance",
        "## 12. Evidence",
    ]
    for section in required:
        assert section in text, f"Missing section: {section}"


def test_application_inventory_has_minimum_expected_methods():
    path = ROOT / "inventory" / "extendscript" / "application_methods.csv"
    assert path.exists(), "Application methods inventory is missing"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    members = {row["member"] for row in rows}
    expected = {
        "app.enableQE",
        "app.openDocument",
        "app.newProject",
        "app.quit",
        "app.setExtensionPersistent",
    }
    assert expected.issubset(members)


def test_application_inventory_has_minimum_expected_attributes():
    path = ROOT / "inventory" / "extendscript" / "application_attributes.csv"
    assert path.exists(), "Application attributes inventory is missing"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    members = {row["member"] for row in rows}
    expected = {
        "app.project",
        "app.projects",
        "app.version",
        "app.build",
        "app.encoder",
    }
    assert expected.issubset(members)


def test_enable_qe_method_contract_exists():
    path = ROOT / "developer_reference" / "extendscript" / "Application" / "Methods" / "enableQE.md"
    assert path.exists(), "enableQE method contract is missing"
    text = path.read_text(encoding="utf-8")
    assert "# app.enableQE()" in text
    assert "## Production notes" in text
    assert "QE DOM" in text
