from pathlib import Path
import json, re

def write_artifacts(project, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    ast={'project':project.name,'node_count':len(project.nodes),'nodes':[{'id':n.id,'kind':n.kind,'title':n.title,'data':n.data,'links':n.links} for n in project.nodes]}
    (out_dir/'knowledge_ast.json').write_text(json.dumps(ast,ensure_ascii=False,indent=2),encoding='utf-8')
    graph={'nodes':[{'id':n.id,'label':n.title,'kind':n.kind} for n in project.nodes],'edges':[]}
    for n in project.nodes:
        for l in n.links: graph['edges'].append({'source':n.id,'target':l['target'],'type':l['type']})
    (out_dir/'knowledge_graph.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2),encoding='utf-8')
    rules=[{'id':n.id,'title':n.title,'severity':n.data.get('severity','info'),'rule':n.data.get('rule') or n.data.get('summary'),'prevents':n.data.get('prevents',[])} for n in project.nodes if n.kind=='rule']
    (out_dir/'ai_rulepack.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
    digital={'objects':[n.data for n in project.nodes if n.kind=='object'],'api':[n.data for n in project.nodes if n.kind=='api'],'serialization':[n.data for n in project.nodes if n.kind=='serialization']}
    (out_dir/'digital_twin.json').write_text(json.dumps(digital,ensure_ascii=False,indent=2),encoding='utf-8')
    tests=[n.data for n in project.nodes if n.kind in ('test','benchmark','evaluation')]
    (out_dir/'test_manifest.json').write_text(json.dumps(tests,ensure_ascii=False,indent=2),encoding='utf-8')
    q={}
    for n in project.nodes:
        tokens=set(re.findall(r'[A-Za-z0-9_\-]+', (n.id+' '+n.title+' '+json.dumps(n.data,ensure_ascii=False)).lower()))
        for tok in tokens: q.setdefault(tok,[]).append(n.id)
    (out_dir/'query_index.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
    kinds={}
    for n in project.nodes: kinds[n.kind]=kinds.get(n.kind,0)+1
    coverage={'node_count':len(project.nodes),'kind_counts':kinds,'rule_count':len(rules),'test_count':len(tests),'graph_edges':len(graph['edges']),'status':'foundation'}
    (out_dir/'coverage_report.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')

def write_rag(markdown_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    fp=out_dir/'rag_chunks.jsonl'
    with fp.open('w',encoding='utf-8') as f:
        for p in sorted(markdown_dir.rglob('*.md')):
            text=p.read_text(encoding='utf-8')
            paras=[x.strip() for x in text.split('\n\n') if x.strip()]
            for i,para in enumerate(paras):
                f.write(json.dumps({'source':p.relative_to(markdown_dir).as_posix(),'chunk':i,'text':para},ensure_ascii=False)+'\n')
