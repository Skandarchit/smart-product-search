"""Optional extension: minimum-degree B-tree insertion/search, not disk storage."""
from dataclasses import dataclass, field
from bisect import bisect_left
from .models import money

@dataclass
class Node:
    keys: list = field(default_factory=list)
    buckets: list = field(default_factory=list)
    children: list = field(default_factory=list)

class BTree:
    def __init__(self, degree=3):
        if degree < 2: raise ValueError("Minimum degree is 2")
        self.degree, self.root = degree, Node()

    def _find(self, key):
        node = self.root
        while True:
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key: return node, i
            if not node.children: return None
            node = node.children[i]

    def search_price(self, price):
        found = self._find(money(price))
        return list(found[0].buckets[found[1]]) if found else []

    def _split(self, parent, i):
        t, full = self.degree, parent.children[i]
        right = Node(full.keys[t:], full.buckets[t:], full.children[t:] if full.children else [])
        parent.keys.insert(i, full.keys[t-1]); parent.buckets.insert(i, full.buckets[t-1])
        parent.children.insert(i+1, right)
        full.keys, full.buckets = full.keys[:t-1], full.buckets[:t-1]
        if full.children: full.children = full.children[:t]

    def insert(self, product):
        found = self._find(product.price)
        if found:
            found[0].buckets[found[1]].append(product); return
        if len(self.root.keys) == 2*self.degree-1:
            self.root = Node(children=[self.root]); self._split(self.root, 0)
        node = self.root
        while node.children:
            i = bisect_left(node.keys, product.price)
            if len(node.children[i].keys) == 2*self.degree-1:
                self._split(node, i)
                if product.price > node.keys[i]: i += 1
            node = node.children[i]
        i = bisect_left(node.keys, product.price)
        node.keys.insert(i, product.price); node.buckets.insert(i, [product])

    def inorder(self):
        def walk(node):
            for i, bucket in enumerate(node.buckets):
                if node.children: yield from walk(node.children[i])
                yield from bucket
            if node.children: yield from walk(node.children[-1])
        yield from walk(self.root)
