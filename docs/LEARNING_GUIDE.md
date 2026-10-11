> Historical Session 1 reference. For current scope, costs and status, read README.md and IMPLEMENTATION_STATUS.md.

> Historical Session 1 reference. For current scope, costs and status, read README.md and IMPLEMENTATION_STATUS.md.

# Session 1 learning guide

## Bottom-up walkthrough

Start with a Product: `P001`, Wireless Headphones, 2499.00, Electronics > Audio > Headphones. The extra ID lets two products share a price or name while remaining individually deletable. Decimal prices avoid binary floating-point money comparisons. The sample data is illustrative.

A linked-list node contains one product and a pointer to its next node. Appending updates the old tail's next pointer and then the tail itself. On an empty list, head and tail both become the new node. Traversal follows next pointers until None. To delete a middle node, connect its previous node directly to its next node; head and tail require special handling.

```text
Before: head -> P001 -> P002 -> P003 -> None
Delete P002:    P001.next = P003
After:  head -> P001 --------> P003 -> None
```

A price BST compares a new price to the current node. Smaller values go left; larger values go right. Equal values join that node's product bucket. A search follows just one branch until a matching price or an empty link. Inorder visits left, current bucket, right and therefore emits products by ascending price. The explicit stack avoids Python's recursion limit on a tall tree.

```text
Insert prices 20, 10, 30, 20:
           20 [two products]
          /  \
        10    30
Inorder: 10, 20, 20, 30
```

## Three-level category hierarchy

This is a general tree with multiple children, separate from the binary price index. There is no counted Catalog root; each path has exactly three category levels. Preorder emits a parent before its children, making indentation easy to draw. Siblings retain first-seen order. A leaf category can contain several products; products are not a fourth category level.

```text
Electronics
    Mobiles
        Smartphones
        Feature Phones
    Audio
        Headphones
        Speakers
Home
    Kitchen
        Bottles
        Cookware
```

The program prints the complete hierarchy, including the other sample paths.

## Query flow

```text
CLI or Streamlit -> Catalog
  name/category -> linked-list traversal -> matching products
  exact price   -> price BST branch walk -> matching price bucket
  sort by price -> BST inorder traversal -> ascending products
  delete by ID  -> linked-list rewiring -> rebuild price index
```

## Complexity reference

Let n be records, h BST height, and k equal-price matches. These are conceptual comparisons, not measured timings.

- Dynamic array: random access O(1); unsorted search O(n); append amortized O(1); insertion/deletion at an arbitrary position O(n); storage O(n).
- Singly linked list with tail: append O(1); search O(n); delete by ID O(n), with O(1) rewiring after locating the node; storage O(n) plus next pointers. Traversal uses O(1) extra space unless results are collected.
- Stack backed by a dynamic array: push amortized O(1), pop/peek at top O(1); arbitrary search/deletion O(n); storage O(n). Use for browsing history or undo. This project uses a Python-list stack internally for inorder; a standalone history/undo stack is not implemented.
- Unbalanced price BST: insertion O(h), exact search O(h + k), native deletion theoretically O(h) before output/bucket handling; storage O(n). This project does not implement native BST deletion. Inorder is O(n) time and O(h) auxiliary stack space. Average logarithmic height requires assumptions about insertion order; worst height is O(n).

At the Catalog service layer, duplicate-ID checking adds O(n) to insertion; deletion rebuilds the index and can take O(nÂ²). These costs must not be confused with low-level pointer operations.

## Choosing structures

Sequential catalogue display suits an array or linked list. Price ordering suits a search tree. Categories suit a general tree. User/product interactions can be represented by a graph. ID lookup can use hashing. Transaction history requires durable storage and ordering; this in-memory example does not provide either persistence or a transaction engine. These are teaching mappings, not claims about Amazon or Flipkart internals. Platform-specific research from Session 1 Task 1 remains a student research activity.

## Six-line learning explanation

Scanning every product makes repeated searches grow with the catalogue.
A suitable index reduces how much data a query must inspect.
A poorly shaped tree can lose the benefit expected from indexing.
Out-of-date indexes can return deleted products or miss new products.
Data structures alone do not ensure useful recommendations or reliable storage.
Correctness tests and representative measurements should guide design choices.

## Try a live Session 1 demo

1. Run `python main.py` and follow the linked-list source alongside the output.
2. Search price 2499 and identify both matches.
3. Launch the UI and insert a new product with an existing price but a new ID.
4. Try inserting the same ID again and observe the validation message.
5. Delete P001; the shoes at 2499 should remain in the price index.
6. Inspect the category diagram and ascending inorder output.
7. Run the timing comparison and explain why a small BST may not win.
8. Run the tests and describe why checking all matches matters.

## Reflection prompts

- Why does deleting the first node need different pointer handling?
- What happens to a price BST when prices arrive in sorted order?
- Why do both searches collect all equal-price products?
- How would an AVL index change search and update trade-offs?
- Why must an index be updated whenever its underlying catalogue changes?

These prompts and sample explanation are learning aids; no personal student reflection or team discussion is claimed.
