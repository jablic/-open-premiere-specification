"""Validate preservation and produce a content-deduplicated source catalog."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]

def audit():
    records = json.loads((ROOT / 'Consolidation/manifest.json').read_text())
    groups = defaultdict(list)
    for record in records:
        if record['disposition'] != 'preserved':
            continue
        path = ROOT / record['destination']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f"Missing or modified preserved source: {record['destination']}")
        groups[record['sha256']].append(record)
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'Sources').rglob('*')
              if p.is_file() and not any(x in p.parts for x in ('__pycache__', '.pytest_cache'))}
    expected = {r['destination'] for group in groups.values() for r in group}
    if actual != expected:
        raise ValueError(f'Uncatalogued source paths: {sorted(actual - expected)}')
    lines = ['# Unique source catalog', '',
             'One entry per SHA-256 content group. Matching bytes are duplicates; matching titles alone are not.', '',
             'These are preserved historical sources, not independently verified API contracts.', '']
    for digest, group in sorted(groups.items(), key=lambda item: item[1][0]['destination']):
        first = group[0]
        lines.append(f"- [{first['destination']}](../{quote(first['destination'])}) — {len(group)} copies; SHA-256 `{digest}`")
        for alias in group[1:]:
            lines.append(f"  - [{alias['destination']}](../{quote(alias['destination'])})")
    catalog = '\n'.join(lines) + '\n'
    return catalog, len(expected), len(groups)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    catalog, files, unique = audit()
    path = ROOT / 'Consolidation/CATALOG.md'
    if args.check:
        if path.read_text() != catalog:
            raise SystemExit('Catalog is stale; run python tools/audit_corpus.py')
    else:
        path.write_text(catalog)
    print(f'Preservation verified: {files} files, {unique} unique contents')
