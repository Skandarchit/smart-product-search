"""One service connects catalog mutation, graph, ranking, cart and UI."""
from .catalog import load_extended,load_retail
from .recommend import demo_graph,Graph
from .rules import evaluate
from .heuristics import explore
from .heaps import top_rated
from pathlib import Path
import json

class SearchEngine:
    def __init__(self,dataset='teaching'):
        self.dataset = dataset
        self.catalog = load_retail() if dataset=='retail' else load_extended()
        self.graph = demo_graph(self.catalog.linked.traverse())
        if dataset=='retail':
            self.graph = Graph()
            for a,b,w in json.loads((Path(__file__).with_name('data')/'retail_interactions.json').read_text()): self.graph.connect(a,b,w)
    def add(self,p): self.catalog.add(p)
    def delete(self,pid):
        removed = self.catalog.delete(pid)
        if removed: self.graph.remove('p:'+pid)
        return removed
    def search(self,name='',category=None): return self.catalog.browse(name,category)
    def recommend(self,start,limit=5):
        rows = self.graph.recommend(start,limit)
        if start not in self.graph.adj:
            return [dict(product_id=p.product_id,name=p.name,score=p.rating,reason='No history: rating fallback; ratings are teaching values') for p in top_rated(self.catalog.by_id.values(),limit)]
        return [dict(**row,name=self.catalog.by_id[row['product_id']].name) for row in rows if row['product_id'] in self.catalog.by_id]
    def rank(self,method='astar',budget=2500,category=None): return explore(list(self.catalog.by_id.values()),method,budget,category)
    def checkout(self,quantities,**profile):
        unknown = set(quantities)-set(self.catalog.by_id)
        if unknown: raise ValueError('Unknown product in cart')
        return evaluate([(self.catalog.by_id[pid],q) for pid,q in quantities.items()],**profile)
