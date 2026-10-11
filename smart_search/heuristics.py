"""BFS, greedy and A* over the same category/product state space.
Preprocessing scores all products; this is an educational search trace, not a
claim of faster retrieval than direct sorting. Each category edge costs one;
a terminal edge costs one plus relevance penalty. A* h is the minimum
remaining product penalty (zero at goals), an admissible lower bound.
"""
import heapq
from collections import deque
import math


def penalty(product,budget=2500,category=None):
    if not math.isfinite(float(budget)) or budget <= 0: raise ValueError('Budget must be positive and finite')
    price = min(abs(float(product.price)-budget)/budget,1)
    rating = 1-product.rating/5
    mismatch = 0 if not category or category in product.category else 1
    return .5*price + .3*rating + .2*mismatch


def explore(products,method='astar',budget=2500,category=None,limit=5):
    if method not in ('bfs','greedy','astar'): raise ValueError('Unknown search method')
    if limit < 0: raise ValueError('Non-negative limit required')
    # Nodes are tuple paths; product leaves include IDs to keep names unique.
    adj = {():[]}; estimates = {}; leaves = {}; scores = {}
    for p in products:
        score = penalty(p,budget,category); scores[p.product_id] = score
        path = ()
        for label in p.category:
            child = path+(label,)
            if child not in adj:
                adj[child] = []; adj[path].append(child)
            estimates[path] = min(estimates.get(path,float('inf')),score)
            path = child
        estimates[path] = min(estimates.get(path,float('inf')),score)
        leaf = path+('ID:'+p.product_id,); adj[path].append(leaf); adj[leaf] = []; leaves[leaf] = p
    frontier = [(0,0,(),0)] if method!='bfs' else deque([((),0)])
    results,trace,counter = [],[],0
    while frontier and len(results)<limit:
        if method=='bfs': node,g = frontier.popleft()
        else: _,_,node,g = heapq.heappop(frontier)
        trace.append({'state':' / '.join(node) or 'Catalog','g':g,'h':0 if node in leaves else estimates.get(node,0)})
        if node in leaves:
            p = leaves[node]; results.append({'product_id':p.product_id,'name':p.name,'penalty':scores[p.product_id],'path_cost':g}); continue
        for child in adj[node]:
            extra = scores[leaves[child].product_id] if child in leaves else 0
            cost = g+1+extra; counter += 1
            if method=='bfs': frontier.append((child,cost))
            else:
                h = 0 if child in leaves else estimates.get(child,0)
                priority = cost+h if method=='astar' else (extra if child in leaves else h)
                heapq.heappush(frontier,(priority,counter,child,cost))
    return {'method':method,'results':results,'expanded':len(trace),'trace':trace,'preprocessed_products':len(scores)}
