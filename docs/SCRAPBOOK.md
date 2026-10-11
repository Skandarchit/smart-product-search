# Algorithm scrapbook

This is a technical learning reference. Add your own team discussions, observations and personal answers.

## Architecture

```text
app.py / main.py
    SearchEngine service
        Catalog -> linked list + ID/category dictionaries
                -> BST + AVL + B-tree price indexes
        Graph -> BFS / DFS / weighted recommendations
        Heuristic search -> category states -> product goals
        Cart -> eight production rules -> priority decision
CSV snapshot -> NumPy/Pandas -> statistics + charts
```

## Search and indexing

Linear search visits each record and collects every exact-name match. It is O(n) even for an early match because this API returns all duplicates. Binary search repeatedly halves the sorted interval to find the left boundary, then collects the k matching entries: O(log n + k). Sorting costs O(n log n) separately. In the 60-name fixture, an absent name still scans all 60 records linearly; binary search needs roughly six halving steps. Exact lookup differs from substring search, which still scans candidates.

The category dictionary maps each one-, two- and three-level prefix to records. Key lookup is average O(1), but copying/processing its k results costs O(k). Comparisons and actual timings for ten queries are in reports/session_experiments.json.

For sorted insertion of prices 0–19, the BST measured 20 nodes in height while AVL measured 5. This is one actual fixture, not a guarantee of a particular speed ratio. AVL keeps subtree heights within one using rotations:

```text
Before left rotation:      After:
1                           2
 \                         / \
  2                       1   3
   \
    3
```

AVL insert/search are O(log n) plus duplicate-result output; unbalanced BST is O(n) worst-case. B-tree splits keep leaf depths equal. Tree updates at the service boundary also maintain other indexes.

## Heaps and graph traversal

A min-heap uses array children 2i+1 and 2i+2 and parent (i-1)//2. Insert appends then bubbles upward; extraction moves the last element to the root then sifts down. Insert/extract are O(log n), peek O(1). A sorted array has O(n) insertion, O(1) minimum peek and O(1) extraction when the minimum is at the end; an unsorted array has amortized O(1) append and O(n) minimum extraction. The max-heap uses negative ratings and stable IDs for ties. Deadline ordering uses parsed ISO datetimes and sequence-number tie breakers.

reports/session_experiments.json records each of 15 min-heap insertion arrays, extracted price order, max-heap rating results and ten scheduled orders. An array level interpretation is index 0; then 1–2; then 3–6; then 7–14.

The teaching graph contains eight users and twelve products. BFS uses a queue for increasing hop distance; DFS uses a stack for deeper exploration. Both ordinary traversals cost O(V+E). Product recommendations select other products within two hops. User recommendations traverse at most three hops and exclude products already linked to that user. Weighted ranking sums the minimum interaction strength on each eligible simple path, so it can revisit paths and costs more than ordinary BFS. Weights are ranking signals, not probabilities. The real-data graph uses observed purchase-line counts; its product count differs from the twelve-product fixture.

## Hashing

The polynomial hash updates h=(31h+ord(character)) mod capacity. Chaining stores explicit linked nodes in each bucket. Linear probing searches successive slots and uses a tombstone on deletion so later collisions remain reachable. Collision reports count occupied nonmatching entries visited during insertion; this is a defined operational metric, not a probability. Twenty names are tested at capacities 23,31,53. These exercises use fixed capacity; probing raises an error when full. Lower load generally reduces probing work. Chaining tolerates load above one at the cost of longer lists. Average dictionary operations are O(1), with O(n) worst cases.

## Informed search

The heuristic penalty is 0.5*bounded relative price distance + 0.3*(1-rating/5) + 0.2*category mismatch. A lower value is preferred. The state tree has three category-filter levels and product leaves. Category edges cost one; the final edge costs one plus product penalty. A* uses g+h, with h equal to the minimum descendant penalty and zero at goals. This is a lower bound because remaining step costs are nonnegative. All product paths have four steps, so terminal cost orders goals by penalty. Greedy prioritizes descendant penalty only; BFS uses FIFO order. The report retains traces, top-five results, node counts and a seeded random baseline.

Scores for all products are precomputed. Fewer expanded states therefore does not establish faster total retrieval. This teaching tree has one path per state and no cycles; a general A* graph requires best-cost tracking and reopening rules. Minimax could model alternating retailer/competitor price choices, but its utility assumptions and branching costs must be justified; implementation is optional and not included.

## Knowledge and rules

The semantic network exposes is-a, has-part, used-with and similar-to triples for fifteen teaching concepts; component and association links are deliberately synthetic examples. Frames express typed slots, defaults and constraints for Laptop, Running Shoes and Cookware. Production rules express conditions and actions separately from evaluation. Their benefits differ: graph relationships aid relational queries, frames validate structured attributes, and rules explain decisions. They still require maintained knowledge and conflict policies.

All eight rules are in rules.py: large cart, electronics, loyal customer, new customer, bulk purchase, home, fashion and SAVE5. The engine returns every applicable rule in priority order but applies only the highest priority, without stacking. This policy is not necessarily the maximum possible discount. Currency mixing and nonpositive quantities are rejected.

## Analytics and integration

The cleaning audit records input types, missing values, output rows and dropped rows. Malformed numeric values are coerced, invalid prices removed, missing categories filled and duplicate IDs resolved. Ratings outside 0–5 become missing. Pandas uses labeled columns/grouping; NumPy handles finite-value masks. Standard deviation uses Pandas' sample convention. Historical revenue uses transaction quantity times transaction unit price, grouped by inferred category/month. Orders count distinct invoice IDs per product, not item quantity.

The three saved charts include interpretation notes. No conclusion about actual satisfaction can be drawn from generated ratings. The 10/100/500/1000 scaling curve includes catalog filtering, row conversion and JSON serialization, excluding UI/network, construction and file reads. Larger result sets require more work. Tests exercise mutation consistency, empty data, duplicate IDs/prices, graph resolution, rule output and analytics.

## Reflection prompts for each session

1. Which pointers change on deletion? Why can a BST become tall? Why does category depth differ from price ordering?
2. Why must binary search be sorted? What does a rotation preserve? What does index maintenance cost?
3. Why is a heap only partially ordered? How do BFS/DFS differ? What does an edge weight mean?
4. How does a tombstone preserve lookup? What happens near full capacity? When is chaining easier?
5. What makes this h admissible? What preprocessing is hidden by node counts? How are rule conflicts resolved?
6. Which fields are observed versus generated? Which rows were removed? Why are sales totals not net revenue?
7. What can break across module boundaries? Which tests detect stale indexes? Which measured cost scales?
8. Can every member explain a module? Can the demo be repeated live? Which limitations must be disclosed?
