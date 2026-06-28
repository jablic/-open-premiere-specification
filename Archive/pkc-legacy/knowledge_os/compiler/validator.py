def validate_project(project):
    errors=[]
    seen=set()
    for n in project.nodes:
        if n.id in seen: errors.append(f'Duplicate id: {n.id}')
        seen.add(n.id)
        if not n.title: errors.append(f'Missing title: {n.id}')
        if not n.kind: errors.append(f'Missing kind: {n.id}')
        if n.kind == 'rule' and not (n.data.get('rule') or n.data.get('summary')):
            errors.append(f'Rule without rule text: {n.id}')
        if n.kind == 'object' and not (n.data.get('ownership') or n.data.get('summary')):
            errors.append(f'Object lacks ownership/summary: {n.id}')
    return errors
