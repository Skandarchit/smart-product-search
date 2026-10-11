import unittest,random,tempfile,json
from pathlib import Path
from smart_search.models import Product
from smart_search.catalog import Catalog,load_extended,load_retail
from smart_search.service import SearchEngine
from smart_search.search import linear_search,binary_search
from smart_search.avl import AVL
from smart_search.btree import BTree
from smart_search.heaps import MinHeap,top_rated,fulfill_orders
from smart_search.hash_tables import ChainingHash,ProbingHash,ProductLookup
from smart_search.heuristics import explore,penalty
from smart_search.knowledge import make_frame,semantic_network
from smart_search.rules import evaluate,RULES


def p(i,price=None): return Product(str(i),f'Item {i}',i if price is None else price,('Home','Kitchen','Cups'),4.0)

class AlgorithmTests(unittest.TestCase):
    def test_avl_all_rotations_and_invariant(self):
        for values in ([3,2,1],[1,2,3],[3,1,2],[1,3,2],list(range(300))):
            tree=AVL()
            for i in values: tree.insert(p(i))
            def check(node):
                if not node:return 0
                left,right=check(node.left),check(node.right)
                self.assertLessEqual(abs(left-right),1);self.assertEqual(node.height,1+max(left,right))
                return node.height
            check(tree.root)
            self.assertEqual([x.price for x in tree.inorder()],sorted(values))

    def test_btree_splits_buckets_and_invariants(self):
        tree=BTree(2);values=list(range(200));random.Random(1).shuffle(values)
        for i in values:tree.insert(p(i))
        tree.insert(p(999,10));depths=set()
        def check(node,depth,is_root=False):
            self.assertEqual(node.keys,sorted(node.keys));self.assertLessEqual(len(node.keys),3)
            if not is_root:self.assertGreaterEqual(len(node.keys),1)
            if node.children:
                self.assertEqual(len(node.children),len(node.keys)+1)
                for child in node.children:check(child,depth+1)
            else:depths.add(depth)
        check(tree.root,0,True);self.assertEqual(len(depths),1)
        self.assertEqual(len(list(tree.inorder())),201)
        self.assertEqual([x.product_id for x in tree.search_price(10)],['10','999'])
        for i in range(200):self.assertEqual(tree.search_price(i)[0],p(i))

    def test_binary_duplicates_empty_and_missing(self):
        rows=[p(2),p(1),Product('3','Item 1',3,('A','B','C'))]
        rows.sort(key=lambda x:x.name.casefold())
        for query in ('Item 1','item 2','missing',''):
            self.assertEqual(binary_search(rows,query),linear_search(rows,query))
        self.assertEqual(binary_search([],''),[])

    def test_heap_and_orders(self):
        heap=MinHeap(); values=[3,1,9,1,0,7]
        for v in values:heap.insert(v)
        self.assertEqual([heap.extract_min() for _ in values],sorted(values))
        with self.assertRaises(IndexError):heap.extract_min()
        orders=[{'deadline':'2026-01-02'},{'deadline':'2026-01-01'}]
        self.assertEqual(fulfill_orders(orders),orders[::-1])
        self.assertEqual(len(top_rated([p(1),p(2)],1)),1)

    def test_hash_collision_update_delete_and_tombstone(self):
        for cls in (ChainingHash,ProbingHash):
            t=cls(3)
            for k,v in [('a',1),('d',2),('g',3)]:t.set(k,v)
            self.assertGreater(t.collisions,0)
            self.assertTrue(t.delete('d'));self.assertEqual(t.get('g'),3)
            t.set('g',4);self.assertEqual(t.size,2);self.assertEqual(t.get('g'),4)
            t.set('j',5);self.assertEqual(t.get('j'),5)
            with self.assertRaises(KeyError):t.get('d')
        with self.assertRaises(OverflowError):t.set('m',6)

    def test_dictionary_crud(self):
        t=ProductLookup();t.insert(p(1));self.assertEqual(t.search('1'),p(1))
        with self.assertRaises(ValueError):t.insert(p(1))
        self.assertEqual(t.delete('1'),p(1));self.assertIsNone(t.search('1'))

    def test_astar_and_greedy_match_sorted_scores(self):
        rows=list(load_extended().by_id.values())
        expected=sorted(penalty(x,2500,'Electronics') for x in rows)[:5]
        for method in ('astar','greedy'):
            result=explore(rows,method,2500,'Electronics')['results']
            self.assertEqual([x['penalty'] for x in result],expected)
        self.assertEqual(explore([])['results'],[])
        with self.assertRaises(ValueError):explore(rows,budget=0)

    def test_frame_constraints_and_concepts(self):
        self.assertEqual(make_frame('Laptop')['ram_gb'],8)
        with self.assertRaises(ValueError):make_frame('Laptop',ram_gb=-1)
        with self.assertRaises(ValueError):make_frame('Laptop',ram_gb='8')
        triples=semantic_network(load_extended().by_id.values())
        self.assertEqual(len({a for a,b,c in triples}),15)
        self.assertEqual({b for a,b,c in triples},{'is-a','has-part','used-with','similar-to'})

class IntegrationTests(unittest.TestCase):
    def setUp(self):self.engine=SearchEngine()
    def test_01_add_updates_every_index(self):
        product=p(999,333);self.engine.add(product);c=self.engine.catalog
        self.assertEqual(c.by_id['999'],product)
        for index in (c.prices,c.avl,c.btree):self.assertIn(product,index.search_price(333))
        self.assertIn(product,c.browse('',('Home',)))
    def test_02_delete_updates_indexes_and_graph(self):
        c=self.engine.catalog;product=c.by_id['X001'];self.engine.delete('X001')
        self.assertNotIn('p:X001',self.engine.graph.adj)
        for index in (c.prices,c.avl,c.btree):self.assertNotIn(product,index.search_price(product.price))
        self.assertNotIn(product,c.browse())
    def test_03_duplicate_id_does_not_mutate(self):
        with self.assertRaises(ValueError):self.engine.add(self.engine.catalog.by_id['X001'])
        self.assertEqual(len(self.engine.catalog.by_id),60)
    def test_04_name_and_category_search(self):
        rows=self.engine.search('PHONE',('Electronics','Mobiles'))
        self.assertTrue(rows);self.assertTrue(all('phone' in p.name.lower() for p in rows))
    def test_05_recommendations_resolve_to_catalog(self):
        rows=self.engine.recommend('p:X001');self.assertTrue(rows)
        self.assertTrue(all(x['product_id'] in self.engine.catalog.by_id and x['product_id']!='X001' for x in rows))
        self.assertEqual(len([n for n in self.engine.graph.adj if n.startswith('u:')]),8)
        self.assertEqual(len([n for n in self.engine.graph.adj if n.startswith('p:')]),12)
    def test_06_user_recommendations_exclude_seen(self):
        rows=self.engine.recommend('u:U01');seen=self.engine.graph.adj['u:U01']
        self.assertTrue(all('p:'+x['product_id'] not in seen for x in rows))
    def test_07_cold_start_fallback(self):self.assertEqual(len(self.engine.recommend('u:NEW')),5)
    def test_08_discounts_priority_and_amount(self):
        result=self.engine.checkout({'X002':1},new=True,coupon='SAVE5')
        self.assertEqual(result['applied'],'Large cart');self.assertEqual(result['payable'],'11049.15')
        self.assertGreaterEqual(len(result['applicable']),3);self.assertEqual(len(RULES),8)
    def test_09_cart_validation_and_empty(self):
        self.assertEqual(self.engine.checkout({})['payable'],'0')
        with self.assertRaises(ValueError):self.engine.checkout({'missing':1})
        with self.assertRaises(ValueError):self.engine.checkout({'X001':0})
        with self.assertRaises(ValueError):self.engine.checkout({},new=True,loyal=True)
    def test_10_analytics_summary(self):
        from smart_search.analytics import load_clean,summarize,sales_summary,filter_products
        df,audit=load_clean();self.assertGreaterEqual(len(df),500)
        overall,grouped=summarize(df);self.assertAlmostEqual(overall.loc['mean','price'],df.price.mean())
        monthly,top,orders=sales_summary(df);self.assertFalse(monthly.empty)
        self.assertLessEqual(len(top),3);self.assertLessEqual(len(orders),5)
        filtered=filter_products(df,0,10,minimum_rating=4)
        self.assertTrue((filtered.price<=10).all());self.assertTrue((filtered.rating>=4).all())
    def test_11_real_catalog_and_graph(self):
        engine=SearchEngine('retail');self.assertGreaterEqual(len(engine.catalog.by_id),500)
        self.assertTrue(all(p.currency=='GBP' for p in engine.catalog.by_id.values()))
        for a,neighbors in engine.graph.adj.items():
            if a.startswith('p:'):self.assertIn(a[2:],engine.catalog.by_id)
    def test_12_term_counter(self):
        self.engine.search(' PHONE ');self.engine.search('phone')
        self.assertEqual(self.engine.catalog.terms['phone'],2)
    def test_13_currency_guard(self):
        with self.assertRaises(ValueError):self.engine.add(Product('G','GBP product',1,('A','B','C'),4,'GBP'))
    def test_14_empty_catalog_flow(self):
        self.engine.catalog=Catalog();self.assertEqual(self.engine.search('x'),[])
        self.assertFalse(self.engine.delete('x'));self.assertEqual(self.engine.rank()['results'],[])
    def test_15_cleaning_malformed_rows(self):
        from smart_search.analytics import load_clean
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'bad.csv';path.write_text('product_id,name,price,category,rating\n1,Good,10,Home,4\n2,Bad,-1,Home,4\n3,Unknown,bad,,8\n1,Updated,12,Home,3\n')
            df,audit=load_clean(path);self.assertEqual(len(df),1);self.assertEqual(df.iloc[0]['price'],12)
            self.assertEqual(audit['dropped_rows'],3)

if __name__=='__main__':unittest.main()
