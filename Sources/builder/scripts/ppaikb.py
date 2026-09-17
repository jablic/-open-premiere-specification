#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path
from datetime import datetime

ROOT_DIRS = ['docs','tools','build','build/rag','build/graph','build/reports','tests','datasets','.github/workflows']
REQUIREMENTS = "mkdocs>=1.6.0\nmkdocs-material>=9.5.0\n"
GITIGNORE = "site/\nbuild/reports/*.tmp\n__pycache__/\n.DS_Store\n.venv/\n"
WORKFLOW = """name: Validate PPAIKB

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python tools/ppaikb.py build
      - run: python tools/ppaikb.py validate
      - run: python tools/ppaikb.py rag
      - run: mkdocs build --strict
"""

def get_seed_docs() -> dict[str,str]:
    here = Path(__file__).resolve().parent
    seed = here / 'seed_docs.json'
    return json.loads(seed.read_text(encoding='utf-8'))

def write(path: Path, content: str, force=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return False
    path.write_text(content, encoding='utf-8')
    return True

def title_from(path: Path):
    return ' '.join(path.stem.replace('-', ' ').replace('_',' ').split()).title()

def scan_docs(root: Path):
    docs=root/'docs'
    return sorted([p for p in docs.rglob('*.md') if p.is_file()], key=lambda p: str(p.relative_to(docs)))

def make_nav_tree(paths):
    tree={}
    for p in paths:
        cur=tree
        for part in p.parts[:-1]: cur=cur.setdefault(part,{})
        cur[p.parts[-1]]=str(p)
    return tree

def nav_yaml_from_tree(tree, indent=2):
    lines=[]
    for key,val in tree.items():
        if isinstance(val, dict):
            lines.append(' '*indent+f'- {key.replace("_"," ").replace("-"," ")}:')
            lines.extend(nav_yaml_from_tree(val, indent+2))
        else:
            label=Path(key).stem.replace('-', ' ').replace('_',' ')
            if key.lower()=='readme.md': label='Overview'
            if key.lower()=='index.md': label='Home'
            lines.append(' '*indent+f'- {label}: {val}')
    return lines

def build_mkdocs(root: Path):
    docs=root/'docs'
    paths=[p.relative_to(docs) for p in scan_docs(root)]
    paths=sorted(paths, key=lambda p:(0 if str(p)=='index.md' else 1, str(p)))
    nav='\n'.join(nav_yaml_from_tree(make_nav_tree(paths)))
    yml=f"""site_name: Premiere Pro Open AI Specification
site_description: AI-native specification and knowledge base for Adobe Premiere Pro automation.
site_url: http://127.0.0.1:8000/
docs_dir: docs
site_dir: site
theme:
  name: material
  language: en
  features:
    - navigation.sections
    - navigation.expand
    - content.code.copy
markdown_extensions:
  - admonition
  - toc:
      permalink: true
  - tables
nav:
{nav}
"""
    write(root/'mkdocs.yml', yml, force=True)

def parse_frontmatter(text):
    if not text.startswith('---'): return {}
    end=text.find('\n---',3)
    if end==-1: return {}
    d={}
    for line in text[3:end].strip().splitlines():
        if ':' in line:
            k,v=line.split(':',1); d[k.strip()]=v.strip().strip('"')
    return d

def build_index(root: Path):
    items=[]; docs_root=root/'docs'
    for p in scan_docs(root):
        text=p.read_text(encoding='utf-8'); fm=parse_frontmatter(text)
        title=fm.get('title') or next((l[2:].strip() for l in text.splitlines() if l.startswith('# ')), title_from(p))
        items.append({'id':fm.get('id',''), 'title':title, 'path':str(p.relative_to(docs_root)), 'section':fm.get('section','')})
    write(root/'build'/'index.json', json.dumps(items, indent=2, ensure_ascii=False), force=True)
    lines=['# Repository Index','']+[f'- [{i["title"]}]({i["path"]}) `{i["id"]}`' for i in items]
    write(root/'docs'/'INDEX.md', '\n'.join(lines)+'\n', force=True)

def build_graph(root: Path):
    docs_root=root/'docs'; nodes=[]; edges=[]; link_re=re.compile(r'\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)')
    for p in scan_docs(root):
        rel=str(p.relative_to(docs_root)); text=p.read_text(encoding='utf-8'); fm=parse_frontmatter(text)
        nodes.append({'id':fm.get('id') or rel, 'path':rel, 'title':fm.get('title') or title_from(p)})
        for m in link_re.finditer(text): edges.append({'source':rel, 'target':m.group(1).split('#')[0], 'type':'markdown_link'})
    graph={'generated_at':datetime.utcnow().isoformat()+'Z','nodes':nodes,'edges':edges}
    write(root/'build'/'graph'/'knowledge_graph.json', json.dumps(graph, indent=2, ensure_ascii=False), force=True)

def chunk_for_rag(root: Path, max_chars=1400):
    docs_root=root/'docs'; out=[]
    for p in scan_docs(root):
        text=p.read_text(encoding='utf-8'); fm=parse_frontmatter(text)
        clean=re.sub(r'^---[\s\S]*?---\n','',text).strip()
        paras=[x.strip() for x in re.split(r'\n\s*\n', clean) if x.strip()]
        buf=''; idx=0
        for para in paras:
            if len(buf)+len(para)+2>max_chars and buf:
                out.append({'doc_id':fm.get('id',''), 'title':fm.get('title',''), 'path':str(p.relative_to(docs_root)), 'chunk_index':idx, 'text':buf}); idx+=1; buf=''
            buf=(buf+'\n\n'+para).strip()
        if buf: out.append({'doc_id':fm.get('id',''), 'title':fm.get('title',''), 'path':str(p.relative_to(docs_root)), 'chunk_index':idx, 'text':buf})
    path=root/'build'/'rag'/'chunks.jsonl'; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in out)+'\n', encoding='utf-8')

def validate(root: Path):
    errors=[]; docs=root/'docs'
    if not (docs/'index.md').exists(): errors.append('Missing docs/index.md')
    mk=root/'mkdocs.yml'
    if mk.exists():
        for line in mk.read_text(encoding='utf-8').splitlines():
            m=re.match(r'\s*-\s+[^:]+:\s+(.+\.md)\s*$', line)
            if m and not (docs/m.group(1)).exists(): errors.append(f'MkDocs nav points to missing file: {m.group(1)}')
    report='\n'.join(errors) if errors else 'OK: validation passed.\n'
    write(root/'build'/'reports'/'validation.txt', report, force=True)
    print(report)
    return 1 if errors else 0

def init_repo(target: Path, force=False):
    if target.exists() and force: shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for d in ROOT_DIRS: (target/d).mkdir(parents=True, exist_ok=True)
    write(target/'requirements.txt', REQUIREMENTS, force=True)
    write(target/'.gitignore', GITIGNORE, force=True)
    write(target/'.github/workflows/validate.yml', WORKFLOW, force=True)
    # Copy self-contained builder package into tools so ppaikb.py can find seed docs.
    tools_pkg = target/'tools'/'ppaikb_builder'
    if tools_pkg.exists(): shutil.rmtree(tools_pkg)
    shutil.copytree(Path(__file__).resolve().parent, tools_pkg)
    write(target/'tools'/'ppaikb.py', "#!/usr/bin/env python3\nfrom ppaikb_builder.cli import main\nif __name__ == '__main__': main()\n", force=True)
    for rel,content in get_seed_docs().items(): write(target/'docs'/rel, content, force=False)
    build_index(target); build_graph(target); chunk_for_rag(target); build_mkdocs(target)
    print(f'Initialized PPAIKB repository at: {target}')

def main(argv=None):
    ap=argparse.ArgumentParser(prog='ppaikb'); sub=ap.add_subparsers(dest='cmd', required=True)
    p=sub.add_parser('init'); p.add_argument('--target', required=True); p.add_argument('--force', action='store_true')
    sub.add_parser('build'); sub.add_parser('validate'); sub.add_parser('rag'); sub.add_parser('graph')
    args=ap.parse_args(argv)
    if args.cmd=='init': init_repo(Path(args.target).expanduser(), args.force)
    elif args.cmd=='build': root=Path.cwd(); build_index(root); build_graph(root); chunk_for_rag(root); build_mkdocs(root); print('Build complete.')
    elif args.cmd=='validate': sys.exit(validate(Path.cwd()))
    elif args.cmd=='rag': chunk_for_rag(Path.cwd()); print('RAG chunks generated.')
    elif args.cmd=='graph': build_graph(Path.cwd()); print('Knowledge graph generated.')
if __name__=='__main__': main()
