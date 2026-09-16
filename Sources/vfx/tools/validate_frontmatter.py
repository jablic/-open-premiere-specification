#!/usr/bin/env python3
"""Validate YAML frontmatter in Knowledge docs"""

import yaml
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path("Knowledge")
errors = []
required_fields = {"id", "title", "category", "status", "doc_status"}
valid_status = {"current", "legacy", "deprecated", "undocumented", "mixed"}
valid_doc_status = {"complete", "partial", "stub"}

for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
    try:
        with open(md_file, 'r') as f:
            content = f.read()
        
        if not content.startswith("---"):
            errors.append(f"{md_file.name}: Missing frontmatter delimiter")
            continue
        
        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            errors.append(f"{md_file.name}: Unclosed frontmatter")
            continue
        
        frontmatter = content[3:frontmatter_end].strip()
        data = yaml.safe_load(frontmatter)
        
        if not isinstance(data, dict):
            errors.append(f"{md_file.name}: Invalid YAML")
            continue
        
        missing = required_fields - set(data.keys())
        if missing:
            errors.append(f"{md_file.name}: Missing {missing}")
        
        if data.get("status") not in valid_status:
            errors.append(f"{md_file.name}: Invalid status")
        
        if data.get("doc_status") not in valid_doc_status:
            errors.append(f"{md_file.name}: Invalid doc_status")
    
    except Exception as e:
        errors.append(f"{md_file.name}: {str(e)}")

if errors:
    print("❌ Validation Errors:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)
else:
    total = len(list(KNOWLEDGE_DIR.glob("*.md")))
    print(f"✅ Validated {total} Knowledge docs")
    sys.exit(0)
