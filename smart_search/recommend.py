"""Undirected weighted user/product graph; namespaced IDs prevent collisions."""
from collections import deque, defaultdict

class Graph:
    def __init__(self): self.adj = {}
    def connect(self,a,b,weight=1):
        if weight <= 0: raise ValueError("Positive interaction weight required")
        self.adj.setdefault(a,{})[b] = self.adj.get(a,{}).get(b,0)+weight
        self.adj.setdefault(b,{})[a] = self.adj.get(b,{}).get(a,0)+weight
    def bfs(self,start,max_depth=None):
        if start not in self.adj: return []
        queue = deque([(start,0)]); seen = {start}; output = []
        while queue:
            node,depth = queue.popleft(); output.append((node,depth))
            if max_depth is not None and depth >= max_depth: continue
            for neighbor in self.adj[node]:
                if neighbor not in seen: seen.add(neighbor); queue.append((neighbor,depth+1))
        return output
    def dfs(self,start):
        if start not in self.adj: return []
        stack,seen,output = [start],set(),[]
        while stack:
            node = stack.pop()
            if node in seen: continue
            seen.add(node); output.append(node)
            stack.extend(reversed(list(self.adj[node])))
        return output
    def remove(self,node):
        for neighbor in list(self.adj.get(node,{})): self.adj[neighbor].pop(node,None)
        self.adj.pop(node,None)
    def recommend(self,start,limit=5):
        """Product: two-hop co-interaction. User: three-hop unseen products."""
        depth = 2 if start.startswith('p:') else 3
        eligible = {n for n,d in self.bfs(start,depth) if n.startswith('p:') and n != start}
        if start.startswith('u:'): eligible -= set(self.adj.get(start,{}))
        scores = defaultdict(float)
        def walk(node,remaining,path,strength):
            if node in eligible: scores[node] += strength
            if remaining:
                for neighbor,weight in self.adj.get(node,{}).items():
                    if neighbor not in path: walk(neighbor,remaining-1,path|{neighbor},min(strength,weight))
        walk(start,depth,{start},float('inf'))
        return [{'product_id':n[2:],'score':scores[n],
                 'reason':f'Sum of minimum edge weights along paths of at most {depth} hops'}
                for n in sorted(eligible,key=lambda n:(-scores[n],n))[:limit]]


def demo_graph(products):
    ids = [p.product_id for p in products][:12]; graph = Graph()
    if not ids: return graph
    for user in range(8):
        for offset in (0,1,4): graph.connect(f'u:U{user+1:02}', 'p:'+ids[(user+offset)%len(ids)],offset+1)
    return graph
