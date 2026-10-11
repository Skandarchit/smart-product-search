"""Semantic triples and typed frames are distinct KR representations."""
FRAMES = {
 'Laptop': {'ram_gb':{'type':int,'default':8,'min':1},'storage_gb':{'type':int,'default':256,'min':32}},
 'Running Shoes': {'size':{'type':int,'default':8,'min':1},'material':{'type':str,'default':'mesh'}},
 'Cookware': {'capacity_l':{'type':float,'default':1.0,'min':0.1},'material':{'type':str,'default':'steel'}}
}

def make_frame(kind,**slots):
    schema = FRAMES[kind]
    if set(slots)-set(schema): raise ValueError('Unknown frame slot')
    result = {}
    for key,spec in schema.items():
        value = slots.get(key,spec['default'])
        if type(value) is not spec['type']: raise ValueError(f'{key} needs {spec["type"].__name__}')
        if 'min' in spec and value<spec['min']: raise ValueError(f'{key} is below minimum')
        result[key] = value
    return result


def semantic_network(products):
    triples = []
    products = list(products)[:15]
    for i,p in enumerate(products):
        triples.append((p.name,'is-a',p.category[-1]))
        triples.append((p.name,'has-part','Component '+str(i+1)))
        if len(products)>1:
            triples.append((p.name,'used-with',products[(i+1)%len(products)].name))
            triples.append((p.name,'similar-to',products[(i+2)%len(products)].name))
    return triples
