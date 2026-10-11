"""Reproducible measurements and traces for the coursework exercises."""
from pathlib import Path
from time import perf_counter_ns
from statistics import median
import json,random,csv
from .catalog import load_extended,Catalog
from .models import Product
from .search import linear_search,binary_search
from .bst import PriceBST
from .avl import AVL,height
from .heaps import MinHeap,top_rated,fulfill_orders
from .hash_tables import ChainingHash,ProbingHash
from .recommend import demo_graph
from .heuristics import explore
from .knowledge import semantic_network,FRAMES,make_frame
from .rules import evaluate


def time_call(fn,repeats=100):
    samples=[]
    fn()
    for _ in range(5):
        start=perf_counter_ns()
        for _ in range(repeats): fn()
        samples.append((perf_counter_ns()-start)/repeats)
    return median(samples)


def bst_height(root):
    stack=[(root,1)] if root else []; maximum=0
    while stack:
        node,depth=stack.pop(); maximum=max(maximum,depth)
        for child in (node.left,node.right):
            if child: stack.append((child,depth+1))
    return maximum


def depth_of(root,key):
    depth=0
    while root:
        depth+=1; value=root.key if hasattr(root,'key') else root.price
        if key==value: return depth
        root=root.left if key<value else root.right
    return depth


def run(output='reports'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    products=list(load_extended().linked.traverse()); names=sorted(products,key=lambda p:p.name.casefold())
    queries=[names[i].name for i in (0,5,10,15,20,25,30,40,59)]+['Missing product']
    searches=[]
    for q in queries:
        assert linear_search(names,q)==binary_search(names,q)
        searches.append({'query':q,'linear_ns':time_call(lambda:linear_search(names,q)),'binary_ns':time_call(lambda:binary_search(names,q))})
    cat=Catalog(products); category=products[0].category
    category_timing={'linear_ns':time_call(lambda:[p for p in products if p.category==category]),'dictionary_ns':time_call(lambda:list(cat.by_category.get(category,[])))}
    bst,avl=PriceBST(),AVL()
    ordered=[Product(f'T{i:02}',f'Sorted product {i:02}',i,('Demo','Sorted','Prices')) for i in range(20)]
    for p in ordered: bst.insert(p);avl.insert(p)
    trees={'bst_height':bst_height(bst.root),'avl_height':height(avl.root),'height_unit':'nodes','search_depths':[{'price':str(p.price),'bst':depth_of(bst.root,p.price),'avl':depth_of(avl.root,p.price)} for p in ordered]}
    heap=MinHeap(key=lambda p:(p.price,p.product_id));steps=[]
    for p in products[:15]: heap.insert(p); steps.append([x.product_id for x in heap.items])
    extracted=[heap.extract_min().row() for _ in range(15)]
    orders=json.loads((Path(__file__).with_name('data')/'orders.json').read_text())
    collisions=[]
    for capacity in (23,31,53):
        for cls in (ChainingHash,ProbingHash):
            table=cls(capacity)
            for p in products[:20]: table.set(p.name,p)
            collisions.append({'strategy':cls.__name__,'capacity':capacity,'products':20,'load_factor':20/capacity,'collisions':table.collisions,'collisions_per_insert':table.collisions/20})
    graph=demo_graph(products);start='p:'+products[0].product_id
    heuristics=[explore(products,m,2500,'Electronics') for m in ('bfs','greedy','astar')]
    shuffled=list(products);random.Random(42).shuffle(shuffled)
    report={'dataset':'60 synthetic teaching products; fixed random seed 42','timing_unit':'median nanoseconds per call, 5 rounds of 100; construction excluded',
       'searches_10_queries':searches,'category_index':category_timing,'sorted_20_tree_comparison':trees,
       'heap_insert_arrays':steps,'heap_extract_sorted':extracted,'rating_max_heap':[p.row() for p in top_rated(products[:15],15)],'orders_10':fulfill_orders(orders),
       'hash_collisions':collisions,'graph_adjacency':graph.adj,'bfs_product_2_hops':graph.bfs(start,2),'dfs_user':graph.dfs('u:U01'),'recommendations':graph.recommend(start),
       'heuristic_search':heuristics,'random_baseline':[p.product_id for p in shuffled[:5]],'semantic_network_15':semantic_network(products),
       'frame_examples':{kind:make_frame(kind) for kind in FRAMES},'discount':evaluate([(products[1],2)],new=True,coupon='SAVE5')}
    (out/'session_experiments.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    sizes=[]
    for n in (10,100,500,1000):
        records=[Product(f'S{i}',products[i%60].name,products[i%60].price,products[i%60].category,products[i%60].rating) for i in range(n)]
        catalog=Catalog(records)
        def request():
            matches=catalog.browse('Phone',('Electronics',))
            return json.dumps([p.row() for p in matches])
        sizes.append({'products':n,'median_ms':time_call(request)/1e6})
    with (out/'query_scaling.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['products','median_ms']);w.writeheader();w.writerows(sizes)
    fig,ax=plt.subplots(figsize=(8,4));ax.plot([v['products'] for v in sizes],[v['median_ms'] for v in sizes],marker='o');ax.set(title='Catalog query through JSON response',xlabel='Catalog products',ylabel='Median milliseconds');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'query_scaling.png',dpi=150);plt.close(fig)
    (out/'performance_notes.txt').write_text('Measured service path: category-index lookup, case-insensitive substring filtering, Product.row conversion and JSON serialization. Excludes index build, browser/network and disk. Five rounds of 100 calls; median. Returning more matches increases scan/serialization work. Larger cases are deterministic synthetic expansions, not observed retail populations. Dictionary category lookup narrows the scan but does not make the whole response constant-time. Profile mutations separately: unbalanced BST build and rebuild-on-delete can be quadratic.\n',encoding='utf-8')
    return {'output':str(out),'tree_heights':trees,'scaling':sizes}
