from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]


def test_developer_reference_core_files_exist():
    required = [
        "developer_reference/README.md",
        "developer_reference/MASTER_TABLE_OF_CONTENTS.md",
        "developer_reference/STYLE_GUIDE.md",
        "developer_reference/EVIDENCE_POLICY.md",
        "developer_reference/METHOD_CONTRACT_TEMPLATE.md",
        "developer_reference/OBJECT_REFERENCE_TEMPLATE.md",
        "developer_reference/TERMINOLOGY.md",
        "developer_reference/VERSION_POLICY.md",
        "developer_reference/INVENTORY_PLAN.md",
        "developer_reference/sources/PRIMARY_SOURCES.md",
        "inventory/surfaces.yaml",
        "inventory/extendscript/objects.csv",
        "inventory/extendscript/methods.csv",
        "inventory/cep/core.csv",
        "inventory/uxp/core.csv",
        "inventory/sdk/core.csv",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing, f"Missing developer reference files: {missing}"


def test_inventory_csv_files_have_required_columns():
    csv_files = [
        ROOT / "inventory/extendscript/objects.csv",
        ROOT / "inventory/extendscript/methods.csv",
        ROOT / "inventory/cep/core.csv",
        ROOT / "inventory/uxp/core.csv",
        ROOT / "inventory/sdk/core.csv",
    ]
    required = {"id", "surface", "kind", "name", "status", "reference_status", "evidence"}
    for path in csv_files:
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames is not None, f"No header in {path}"
            assert required.issubset(set(reader.fieldnames)), f"Missing columns in {path}: {required - set(reader.fieldnames)}"
            rows = list(reader)
            assert rows, f"Inventory file is empty: {path}"
            assert all(row["id"].strip() for row in rows), f"Empty id in {path}"
