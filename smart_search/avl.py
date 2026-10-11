"""Session 2: AVL insertion with explicit rotations and price buckets."""
from dataclasses import dataclass, field
from .models import money

@dataclass
class Node:
    key: object
    products: list = field(default_factory=list)
    left: object = None
    right: object = None
    height: int = 1


def height(node): return node.height if node else 0

def refresh(node): node.height = 1 + max(height(node.left), height(node.right))

def right_rotate(y):
    x, middle = y.left, y.left.right
    x.right, y.left = y, middle
    refresh(y); refresh(x)
    return x

def left_rotate(x):
    y, middle = x.right, x.right.left
    y.left, x.right = x, middle
    refresh(x); refresh(y)
    return y


class AVL:
    def __init__(self): self.root = None

    def insert(self, product):
        def add(node):
            if node is None: return Node(product.price, [product])
            if product.price == node.key:
                node.products.append(product); return node
            if product.price < node.key: node.left = add(node.left)
            else: node.right = add(node.right)
            refresh(node)
            balance = height(node.left) - height(node.right)
            if balance > 1:
                if product.price > node.left.key: node.left = left_rotate(node.left)
                return right_rotate(node)
            if balance < -1:
                if product.price < node.right.key: node.right = right_rotate(node.right)
                return left_rotate(node)
            return node
        self.root = add(self.root)

    def search_price(self, price):
        key, node = money(price), self.root
        while node:
            if key == node.key: return list(node.products)
            node = node.left if key < node.key else node.right
        return []

    def inorder(self):
        def walk(node):
            if node:
                yield from walk(node.left)
                yield from node.products
                yield from walk(node.right)
        yield from walk(self.root)
