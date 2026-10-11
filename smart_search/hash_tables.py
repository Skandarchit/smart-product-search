"""Teaching hash tables. Collision metric: occupied nonmatching slots visited."""
from dataclasses import dataclass

def string_hash(key, capacity):
    h = 0
    for character in key: h = (31*h + ord(character)) % capacity
    return h

@dataclass
class Entry:
    key: str
    value: object
    next: object = None

class ChainingHash:
    def __init__(self, capacity=31):
        if capacity < 1: raise ValueError("Positive capacity required")
        self.buckets = [None]*capacity; self.collisions = 0; self.size = 0
    def set(self, key, value):
        i = string_hash(key,len(self.buckets)); node = self.buckets[i]
        while node:
            if node.key == key: node.value = value; return
            self.collisions += 1; node = node.next
        self.buckets[i] = Entry(key,value,self.buckets[i]); self.size += 1
    def get(self, key):
        node = self.buckets[string_hash(key,len(self.buckets))]
        while node:
            if node.key == key: return node.value
            node = node.next
        raise KeyError(key)
    def delete(self, key):
        i = string_hash(key,len(self.buckets)); previous = None; node = self.buckets[i]
        while node:
            if node.key == key:
                if previous: previous.next = node.next
                else: self.buckets[i] = node.next
                self.size -= 1; return True
            previous, node = node, node.next
        return False

_DELETED = object()
class ProbingHash:
    def __init__(self, capacity=31):
        if capacity < 1: raise ValueError("Positive capacity required")
        self.slots = [None]*capacity; self.collisions = 0; self.size = 0
    def set(self, key, value):
        start = string_hash(key,len(self.slots)); free = None
        for offset in range(len(self.slots)):
            i = (start+offset)%len(self.slots); slot = self.slots[i]
            if slot is None:
                if free is None: free = i
                break
            if slot is _DELETED:
                if free is None: free = i
            elif slot[0] == key: self.slots[i] = (key,value); return
            else: self.collisions += 1
        if free is None: raise OverflowError("Hash table full")
        self.slots[free] = (key,value); self.size += 1
    def _locate(self, key):
        start = string_hash(key,len(self.slots))
        for offset in range(len(self.slots)):
            i = (start+offset)%len(self.slots); slot = self.slots[i]
            if slot is None: break
            if slot is not _DELETED and slot[0] == key: return i
        raise KeyError(key)
    def get(self,key): return self.slots[self._locate(key)][1]
    def delete(self,key):
        try: i = self._locate(key)
        except KeyError: return False
        self.slots[i] = _DELETED; self.size -= 1; return True

class ProductLookup:
    """Dictionary-only CRUD: average O(1), independent of other indexes."""
    def __init__(self): self.records = {}
    def insert(self,p):
        if p.product_id in self.records: raise ValueError("Duplicate ID")
        self.records[p.product_id] = p
    def search(self,pid): return self.records.get(pid)
    def delete(self,pid): return self.records.pop(pid,None)
