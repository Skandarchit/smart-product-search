"""Manual min-heap plus heapq-based rating and deadline queues."""
import heapq

class MinHeap:
    def __init__(self, key=lambda x:x): self.items, self.key = [], key
    def insert(self, value):
        self.items.append(value); i = len(self.items)-1
        while i:
            parent = (i-1)//2
            if self.key(self.items[parent]) <= self.key(self.items[i]): break
            self.items[parent], self.items[i] = self.items[i], self.items[parent]
            i = parent
    def peek(self):
        if not self.items: raise IndexError("Empty heap")
        return self.items[0]
    def extract_min(self):
        result = self.peek(); last = self.items.pop()
        if self.items:
            self.items[0] = last; i = 0
            while 2*i+1 < len(self.items):
                child = 2*i+1
                if child+1 < len(self.items) and self.key(self.items[child+1]) < self.key(self.items[child]): child += 1
                if self.key(self.items[i]) <= self.key(self.items[child]): break
                self.items[i], self.items[child] = self.items[child], self.items[i]; i = child
        return result


def top_rated(products, limit=5):
    heap = [(-p.rating, p.product_id, p) for p in products]; heapq.heapify(heap)
    return [heapq.heappop(heap)[2] for _ in range(min(max(0,limit),len(heap)))]


def fulfill_orders(orders):
    """ISO dates sort chronologically; sequence number breaks ties stably."""
    from datetime import datetime
    heap = [(datetime.fromisoformat(o['deadline']),i,o) for i,o in enumerate(orders)]
    heapq.heapify(heap)
    return [heapq.heappop(heap)[2] for _ in range(len(heap))]
