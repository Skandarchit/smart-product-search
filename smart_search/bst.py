"""Unbalanced price BST. Equal prices share a bucket, preserving all matches."""
from dataclasses import dataclass, field
from decimal import Decimal
from .models import Product, money


@dataclass
class PriceNode:
    price: Decimal
    products: list[Product] = field(default_factory=list)
    left: "PriceNode | None" = None
    right: "PriceNode | None" = None


class PriceBST:
    def __init__(self):
        self.root = None

    def insert(self, product):
        if self.root is None:
            self.root = PriceNode(product.price, [product])
            return
        current = self.root
        while True:
            if product.price == current.price:
                current.products.append(product)
                return
            side = "left" if product.price < current.price else "right"
            child = getattr(current, side)
            if child is None:
                setattr(current, side, PriceNode(product.price, [product]))
                return
            current = child

    def search_price(self, price):
        price = money(price)
        current = self.root
        while current is not None:
            if price == current.price:
                return list(current.products)
            current = current.left if price < current.price else current.right
        return []

    def inorder(self):
        """Left, node, right. Explicit stack avoids recursion depth failures."""
        stack = []
        current = self.root
        while stack or current is not None:
            while current is not None:
                stack.append(current)
                current = current.left
            current = stack.pop()
            yield from current.products
            current = current.right
