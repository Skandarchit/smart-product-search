"""Application boundary: mutate through Catalog to keep the two structures synced."""
import json
from pathlib import Path
from .models import Product
from .linked_list import ProductLinkedList
from .bst import PriceBST
from .avl import AVL
from .btree import BTree
from collections import Counter, defaultdict


class Catalog:
    def __init__(self, products=()):
        self.linked = ProductLinkedList()
        self.prices = PriceBST()
        self.avl = AVL()
        self.btree = BTree()
        self.by_id = {}
        self.by_category = defaultdict(list)
        self.terms = Counter()
        for product in products:
            self.add(product)

    def add(self, product):
        if not isinstance(product, Product):
            raise ValueError("Expected a Product")
        if product.product_id in self.by_id:
            raise ValueError("Product ID already exists")
        if self.by_id and product.currency != next(iter(self.by_id.values())).currency:
            raise ValueError("Catalog must use one currency")
        self.linked.insert(product)
        self.prices.insert(product)
        self.avl.insert(product)
        self.btree.insert(product)
        self.by_id[product.product_id] = product
        for depth in (1,2,3): self.by_category[product.category[:depth]].append(product)

    def delete(self, product_id):
        if not self.linked.delete(product_id):
            return False
        self.by_id.pop(product_id)
        self.prices, self.avl, self.btree = PriceBST(), AVL(), BTree()
        self.by_category = defaultdict(list)
        for product in self.linked.traverse():
            self.prices.insert(product); self.avl.insert(product); self.btree.insert(product)
            for depth in (1,2,3): self.by_category[product.category[:depth]].append(product)
        return True

    def browse(self, name="", category=None):
        """Case-insensitive substring scan; category is an exact path prefix."""
        query = name.strip().casefold()
        if query: self.terms[query] += 1
        candidates = self.by_category.get(tuple(category), []) if category else self.linked.traverse()
        return [p for p in candidates
                if query in p.name.casefold()
                and (category is None or p.category[:len(category)] == tuple(category))]


def load_sample():
    path = Path(__file__).with_name("data") / "products.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return Catalog(Product(**record) for record in data)


def load_extended():
    data = json.loads((Path(__file__).with_name("data") / "extended.json").read_text(encoding="utf-8"))
    return Catalog(Product(**record) for record in data)


def load_retail():
    import csv
    path = Path(__file__).with_name("data") / "retail_products.csv"
    with path.open(encoding="utf-8",newline="") as stream:
        return Catalog(Product(row['product_id'],row['name'],row['price'],tuple(row['category'].split(' > ')),float(row['rating']), 'GBP') for row in csv.DictReader(stream))
