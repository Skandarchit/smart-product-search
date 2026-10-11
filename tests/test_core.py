import random
import unittest
from smart_search.models import Product, money
from smart_search.linked_list import ProductLinkedList
from smart_search.bst import PriceBST
from smart_search.catalog import Catalog, load_sample
from smart_search.categories import build_hierarchy, preorder
from smart_search.benchmark import compare


def product(i, price=None):
    return Product(str(i), f"Product {i}", i if price is None else price, ("A", "B", "C"))


class CoreTests(unittest.TestCase):
    def test_sample_minimum_and_fields(self):
        rows = list(load_sample().linked.traverse())
        self.assertGreaterEqual(len(rows), 10)
        self.assertEqual(len(rows), len({p.product_id for p in rows}))
        self.assertTrue(all(len(p.category) == 3 for p in rows))

    def test_validation(self):
        for value in ["nan", "Infinity", "-1", "1.001", "bad", None]:
            with self.subTest(value=value), self.assertRaises(ValueError): money(value)
        with self.assertRaises(ValueError): Product("", "x", 1, ("A", "B", "C"))
        with self.assertRaises(ValueError): Product("x", "x", 1, ("A", "B"))
        self.assertEqual(str(money("0.10")), "0.10")

    def test_empty_structures(self):
        linked, bst = ProductLinkedList(), PriceBST()
        self.assertEqual(list(linked.traverse()), [])
        self.assertFalse(linked.delete("missing"))
        self.assertEqual(bst.search_price(1), [])
        self.assertEqual(list(bst.inorder()), [])

    def test_linked_insertion_order(self):
        linked = ProductLinkedList()
        for i in [3, 1, 2]: linked.insert(product(i))
        self.assertEqual([p.product_id for p in linked.traverse()], ["3", "1", "2"])

    def test_delete_head_middle_tail_and_last(self):
        linked = ProductLinkedList()
        for i in range(4): linked.insert(product(i))
        for i, expected in [(0, [1,2,3]), (2, [1,3]), (3, [1]), (1, [])]:
            self.assertTrue(linked.delete(str(i)))
            self.assertEqual([int(p.product_id) for p in linked.traverse()], expected)
        self.assertIsNone(linked.tail)
        linked.insert(product(8))
        self.assertEqual(list(linked.traverse()), [product(8)])

    def test_duplicate_prices(self):
        catalog = Catalog([product(1, 20), product(2, 20)])
        self.assertEqual(catalog.linked.search_price(20), catalog.prices.search_price(20))
        self.assertEqual(len(catalog.prices.search_price(20)), 2)

    def test_duplicate_id_rejected_atomically(self):
        catalog = Catalog([product(1)])
        with self.assertRaises(ValueError): catalog.add(product(1, 99))
        self.assertEqual(list(catalog.prices.inorder()), [product(1)])

    def test_bst_inorder_against_sorted_oracle(self):
        rng = random.Random(42)
        products = [product(i, rng.randrange(20)) for i in range(200)]
        catalog = Catalog(products)
        self.assertEqual(list(catalog.prices.inorder()), sorted(products, key=lambda p:p.price))
        for value in range(22):
            expected = [p for p in products if p.price == value]
            self.assertEqual(catalog.prices.search_price(value), expected)

    def test_degenerate_bst_is_iterative(self):
        tree = PriceBST()
        for i in range(1100): tree.insert(product(i))
        self.assertEqual(len(list(tree.inorder())), 1100)
        self.assertEqual(tree.search_price(1099), [product(1099)])

    def test_catalog_delete_keeps_index_synced(self):
        catalog = load_sample()
        self.assertTrue(catalog.delete("P001"))
        self.assertEqual([p.product_id for p in catalog.prices.search_price(2499)], ["P006"])
        self.assertFalse(catalog.delete("missing"))
        self.assertEqual(list(catalog.prices.inorder()), sorted(catalog.linked.traverse(),key=lambda p:p.price))

    def test_search_name_and_category(self):
        catalog = load_sample()
        self.assertEqual(len(catalog.browse("  PHONE  ", ("Electronics", "Mobiles"))), 2)
        self.assertEqual(catalog.browse("nonexistent"), [])
        self.assertEqual(len(catalog.browse()), 12)

    def test_category_depth_and_deduplication(self):
        nodes = list(preorder(build_hierarchy([product(1),product(2)])))
        self.assertEqual(nodes, [(0,"A"),(1,"B"),(2,"C")])
        self.assertEqual(build_hierarchy([]), [])

    def test_benchmark_contract(self):
        report = compare(load_sample(), [2499,100], repeats=2, rounds=3)
        self.assertEqual(report["products"], 12)
        for values in report["samples_ns"].values():
            self.assertEqual(len(values), 3)
            self.assertTrue(all(v >= 0 for v in values))
        with self.assertRaises(ValueError): compare(load_sample(), [])

    def test_mutation_sequence_against_oracle(self):
        catalog = Catalog()
        oracle = []
        rng = random.Random(10)
        for i in range(50):
            p = product(i, rng.randrange(10))
            catalog.add(p); oracle.append(p)
            if i % 3 == 0:
                removed = oracle.pop(0)
                self.assertTrue(catalog.delete(removed.product_id))
            self.assertEqual(list(catalog.linked.traverse()), oracle)
            self.assertEqual(list(catalog.prices.inorder()), sorted(oracle,key=lambda p:p.price))

if __name__ == "__main__": unittest.main()
