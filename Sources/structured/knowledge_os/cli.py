from pathlib import Path
import argparse, shutil, subprocess, socket, json
from knowledge_os.compiler.parser import load_project
from knowledge_os.compiler.validator import validate_project
from knowledge_os.generators.markdown import write_markdown
from knowledge_os.generators.artifacts import write_artifacts, write_rag

ROOT = Path(__file__).resolve().parents[1]

def copytree(src, dst, force=False):
    if dst.exists() and force: shutil.rmtree(dst)
    if not dst.exists(): shutil.copytree(src, dst)

def init_premiere(args):
    target=Path(args.target).expanduser()
    if target.exists() and args.force: shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    copytree(ROOT/'plugins'/'premiere'/'spec_src', target/'spec_src', force=True)
    copytree(ROOT/'knowledge_os', target/'knowledge_os', force=True)
    (target/'tools').mkdir(exist_ok=True)
    shutil.copy(ROOT/'tools'/'pkc.py', target/'tools'/'pkc.py')
    (target/'requirements.txt').write_text((ROOT/'requirements.txt').read_text(), encoding='utf-8')
    (target/'README.md').write_text('# Premiere Pro Open AI Specification\n\nRun `python3 tools/pkc.py all`.\n\nMachine-readable artifacts are generated into `build/artifacts/`.\n', encoding='utf-8')
    print(f'Initialized PKC Premiere repository: {target}')

def compile_repo(repo: Path):
    project=load_project(repo/'spec_src')
    errors=validate_project(project)
    if errors:
        print('Validation errors:'); [print(' - '+e) for e in errors]; raise SystemExit(1)
    docs=repo/'docs'; artifacts=repo/'build'/'artifacts'; rag=repo/'build'/'rag'
    if docs.exists(): shutil.rmtree(docs)
    index=write_markdown(project, docs)
    write_artifacts(project, artifacts)
    write_rag(docs, rag)
    mkdocs="site_name: Premiere Pro Open AI Specification\ntheme:\n  name: material\ndocs_dir: docs\nplugins:\n  - search\nnav:\n  - Home: index.md\n"
    for title,path,_id in index:
        mkdocs += f'  - "{str(title).replace(chr(34), chr(39))} {_id}": {path}\n'
    (repo/'mkdocs.yml').write_text(mkdocs, encoding='utf-8')
    print(f'Compiled {len(project.nodes)} DSL specs.')
    print('Generated docs, AST, graph, rulepack, digital twin, query index and RAG chunks.')

def validate_cmd(repo: Path):
    project=load_project(repo/'spec_src')
    errors=validate_project(project)
    if errors:
        print('Validation errors:'); [print(' - '+e) for e in errors]; raise SystemExit(1)
    print('OK: validation passed.')

def stats(repo: Path):
    project=load_project(repo/'spec_src')
    kinds={}
    for n in project.nodes: kinds[n.kind]=kinds.get(n.kind,0)+1
    print('PKC repository stats')
    print(f'Nodes: {len(project.nodes)}')
    for k in sorted(kinds): print(f'  {k}: {kinds[k]}')

def query(repo: Path, text: str):
    project=load_project(repo/'spec_src')
    q=text.lower(); hits=[]
    for n in project.nodes:
        blob=(n.id+' '+n.title+' '+json.dumps(n.data,ensure_ascii=False)).lower()
        if q in blob: hits.append(n)
    for n in hits[:25]: print(f'{n.id}\t{n.kind}\t{n.title}')
    if not hits: print('No matches.')

def serve(repo: Path):
    port=8000
    while port<8020:
        s=socket.socket()
        try: s.bind(('127.0.0.1',port)); s.close(); break
        except OSError: port+=1
    print(f'Serving on http://127.0.0.1:{port}/')
    subprocess.run(['mkdocs','serve','-a',f'127.0.0.1:{port}'], cwd=repo)

def main():
    ap=argparse.ArgumentParser(prog='pkc')
    sub=ap.add_subparsers(dest='cmd')
    p=sub.add_parser('init-premiere'); p.add_argument('--target', required=True); p.add_argument('--force', action='store_true')
    sub.add_parser('compile'); sub.add_parser('all'); sub.add_parser('serve'); sub.add_parser('validate'); sub.add_parser('stats')
    q=sub.add_parser('query'); q.add_argument('text')
    args=ap.parse_args()
    if args.cmd=='init-premiere': init_premiere(args)
    elif args.cmd in ('compile','all'): compile_repo(Path.cwd())
    elif args.cmd=='validate': validate_cmd(Path.cwd())
    elif args.cmd=='stats': stats(Path.cwd())
    elif args.cmd=='query': query(Path.cwd(), args.text)
    elif args.cmd=='serve': serve(Path.cwd())
    else: ap.print_help()
if __name__=='__main__': main()
