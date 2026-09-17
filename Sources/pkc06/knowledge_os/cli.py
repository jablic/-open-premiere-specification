from pathlib import Path
import argparse, shutil, subprocess, socket, os
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
    (target/'tools').mkdir(exist_ok=True)
    shutil.copy(ROOT/'tools'/'pkc.py', target/'tools'/'pkc.py')
    (target/'requirements.txt').write_text((ROOT/'requirements.txt').read_text(), encoding='utf-8')
    (target/'README.md').write_text('# Premiere Pro Open AI Specification\n\nRun `python3 tools/pkc.py all`.\n', encoding='utf-8')
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
    mkdocs = "site_name: Premiere Pro Open AI Specification\ntheme:\n  name: material\ndocs_dir: docs\nnav:\n  - Home: index.md\n"
    for title,path,_id in index:
        safe_title = str(title).replace('"', "'")
        mkdocs += f'  - "{safe_title} {_id}": {path}\n'
    (repo/'mkdocs.yml').write_text(mkdocs, encoding='utf-8')
    print(f'Compiled {len(project.nodes)} DSL specs.')
    print('Generated docs, AST, graph, rulepack, digital twin and RAG chunks.')

def serve(repo: Path):
    port=8000
    while port<8020:
        s=socket.socket()
        try:
            s.bind(('127.0.0.1',port)); s.close(); break
        except OSError: port+=1
    print(f'Serving on http://127.0.0.1:{port}/')
    subprocess.run(['mkdocs','serve','-a',f'127.0.0.1:{port}'], cwd=repo)

def main():
    ap=argparse.ArgumentParser(prog='pkc')
    sub=ap.add_subparsers(dest='cmd')
    p=sub.add_parser('init-premiere'); p.add_argument('--target', required=True); p.add_argument('--force', action='store_true')
    sub.add_parser('compile'); sub.add_parser('all'); sub.add_parser('serve')
    args=ap.parse_args()
    if args.cmd=='init-premiere': init_premiere(args)
    elif args.cmd in ('compile','all'): compile_repo(Path.cwd())
    elif args.cmd=='serve': serve(Path.cwd())
    else: ap.print_help()
if __name__=='__main__': main()
