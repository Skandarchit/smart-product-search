"""Explicit nodes and pointer rewiring: no Python list as primary storage."""
from dataclasses import dataclass
from .models import Product, money


@dataclass
class Node:
    product: Product
    next: "Node | None" = None


class ProductLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert(self, product):
        """Append in O(1). ID uniqueness is the catalogue service's job."""
        node = Node(product)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node

    def traverse(self):
        current = self.head
        while current is not None:
            yield current.product
            current = current.next

    def delete(self, product_id):
        """Find the first matching ID and bypass its node; O(n)."""
        previous = None
        current = self.head
        while current is not None:
            if current.product.product_id == product_id:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                return True
            previous = current
            current = current.next
        return False

    def search_price(self, price):
        price = money(price)
        return [p for p in self.traverse() if p.price == price]
