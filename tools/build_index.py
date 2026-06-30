#!/usr/bin/env python3
"""Generate knowledge base index from frontmatter"""

import yaml
from pathlib import Path

KNOWLEDGE_DIR = Path("Knowledge")

def build_index():
    """Generate index of all Knowledge docs"""
    docs = []
    
    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        with open(md_file, 'r') as f:
            content = f.read()
        
        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            continue
        
        frontmatter = content[3:frontmatter_end].strip()
        data = yaml.safe_load(frontmatter)
        
        docs.append({
            'file': md_file.name,
            'id': data.get('id'),
            'title': data.get('title'),
            'category': data.get('category'),
            'status': data.get('status'),
            'doc_status': data.get('doc_status'),
            'confidence': data.get('confidence')
        })
    
    return docs

if __name__ == "__main__":
    docs = build_index()
    
    print(f"📚 Knowledge Base Index ({len(docs)} docs)")
    print("="*70)
    print()
    
    by_status = {}
    for doc in docs:
        status = doc['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(doc)
    
    for status in ["current", "legacy", "undocumented", "mixed"]:
        if status in by_status:
            print(f"📍 {status.upper()} ({len(by_status[status])} docs)")
            for doc in by_status[status]:
                print(f"  [{doc['doc_status']}] {doc['title']}")
            print()
