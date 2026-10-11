# Live demonstration guide

Run the app before starting and use the bundled reports as evidence, while performing searches live.

- Minutes 0–2: explain the problem and architecture. Show the 60-product teaching catalog and the three-level categories.
- Minutes 2–4: search names and prices; add/delete a product. Explain linked-list storage, ID/category indexes, AVL rotations and the 20-versus-5 height experiment.
- Minutes 4–6: open Recommendations, show a two-hop product result and BFS/DFS traces. Compare BFS, greedy and A* and disclose preprocessing and teaching ratings.
- Minutes 6–8: add X002 to a cart and evaluate the eight rules. Explain why the highest priority applies and why discounts do not stack.
- Minutes 8–10: switch to the UCI catalog. Run a live query and observed graph recommendation. Show analytics and the source/cleaning notes. Distinguish historical observations, inferred categories and generated ratings.
- Minutes 10–12: show the response-time curve and poster, discuss limits, and answer questions.

## Five likely questions

1. Why use a dictionary and a tree? ID lookup needs equality; price indexes illustrate ordered retrieval. The catalog maintains both for different queries.
2. Why use AVL instead of the basic BST? Rotations keep logarithmic height even when keys arrive sorted; they add update bookkeeping.
3. What happens for a new user? The app returns a labeled rating fallback. Here those ratings are teaching data, not verified customer preferences.
4. Does A* make this search faster? Not established. It uses all-product preprocessing; node counts only measure traversal of the constructed state tree.
5. How do deleted products disappear everywhere? The service removes storage/index entries, rebuilds price indexes and removes graph links. The rebuild is simple but expensive at scale.

## Team activities to complete

Record two rehearsal dates, duration and issues. Exchange tests with another team and record reviewer, steps, expected/actual results, severity, fix and retest outcome. Do not present generated tests as an independent peer review.

For each student's 300–500 word reflection, allocate roughly 75 words to the starting understanding, 100 to one concrete implementation/debugging experience, 100 to trade-offs and teamwork, and 75–125 to future applications. Write from actual experience; this project does not invent personal reflections.
