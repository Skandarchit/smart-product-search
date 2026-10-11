# IP project — Smart Product Search

Integrated educational implementation of DOE Sessions 1–8, presented as a simple storefront. Shop shows product cards, plain-language filters and an Add to cart flow. My cart shows quantities, savings and a final demo total. Store overview contains readable search counts and sales summaries. Technical demonstrations and product management are under Coursework.

After updating, stop the old Streamlit process with Ctrl+C and run it again so the new light theme loads. See docs/STOREFRONT.md for the shopping guide.

## Run on Windows

Open PowerShell:

```powershell
cd "$HOME\Desktop\IP project"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the localhost address printed in the terminal. Replace `python` with `py` if Windows requires it. Python 3.10+ is required. Installation needs internet access; normal operation uses bundled local data. Stop the app with Ctrl+C. On macOS/Linux, use `.venv/bin/python` instead.

## Commands

Run from the project folder with the same environment:

```powershell
.\.venv\Scripts\python.exe main.py --demo
.\.venv\Scripts\python.exe main.py --demo --dataset retail
.\.venv\Scripts\python.exe main.py --dataset teaching --name phone
.\.venv\Scripts\python.exe main.py --price 2499
.\.venv\Scripts\python.exe main.py --experiments
.\.venv\Scripts\python.exe main.py --analytics
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The original Session 1 CLI still runs without third-party packages: `python main.py`. The full test suite and analytics need requirements.txt.

## Implemented

- Session 1: 12-record sample, explicit linked list, price BST, category hierarchy and matched search timing.
- Session 2: linear/binary exact-name search on 60 names, 10 timed queries, category dictionary, AVL rotations/inorder, sorted-20 BST/AVL height comparison, educational B-tree insertion/search and a database-index research note.
- Session 3: manual min-heap, rating max-heap, 10-order deadline queue, 8-user/12-product teaching graph, BFS/DFS, weighted recommendations and traces.
- Session 4: polynomial string hash, linked-list chaining, linear probing with tombstones, 20-product collision experiments, dictionary CRUD and top-five search counts.
- Session 5: BFS/greedy/A* comparison over the same category/product space, 15-concept synthetic semantic network, three typed frames, eight discount rules and priority-based inference.
- Session 6: 1,000-product CSV, NumPy/Pandas cleaning, filtering/sorting, overall/category statistics, monthly sales summaries, top categories/products and three chart files.
- Session 7: shared service, 15 integration cases plus algorithm/core/UI tests, query measurements at 10/100/500/1,000 records and a performance plot.
- Session 8: runnable integrated demo, demo guide, five technical Q&A examples, and a one-page technical poster.

## Data and limits

The teaching catalog contains 60 fictional products priced in INR. The UCI catalog contains 1,000 historical UK retail products in GBP and 275,602 retained positive transaction lines. Names, prices, transaction dates and purchase interactions are derived from UCI Online Retail. Category labels are inferred and ratings are synthetic teaching values, explicitly identified in the UI and CSV. Sales totals exclude cancellations/returns; they are not net revenue. See `smart_search/data/retail_provenance.json` and `docs/DATA_AND_SOURCES.md`.

Edits exist only in browser session memory. Switching/resetting datasets restores bundled data. Analytics reads the bundled CSV snapshot rather than in-memory edits. Currency mixing is rejected. Shop search counts increase only when Find products is submitted. Browsing cards, sorting through other pages and updating a cart do not count again. Technical coursework searches do not affect the customer search counter. Generated ratings are hidden from the customer-facing shop.

Delete rebuilds all price/category indexes and removes graph edges. Native tree deletion, persistent storage, login, actual payment handling and deployed production infrastructure are not implemented. The maintained unbalanced BST can still make insertion/rebuild quadratic. The independent dictionary CRUD exercise has average O(1) operations; the whole Catalog service does not.

Heuristic search precomputes relevance over all products; its node count excludes that work. This makes it a transparent state-space exercise, not evidence of a production speed advantage. Cold-start recommendations use teaching ratings. Rule percentages and currency thresholds are illustrative, and only the highest-priority rule applies.

## Files and learning materials

Read `models.py`, `linked_list.py`, `bst.py`, then `avl.py`, `btree.py`, `search.py`, `heaps.py`, `recommend.py`, `hash_tables.py`, `heuristics.py`, `rules.py`, and `analytics.py` inside `smart_search/`. `service.py` integrates the modules; `app.py` and `main.py` provide interfaces.

Generated results are in `reports/`; regenerate them with the commands above. `docs/SCRAPBOOK.md` explains the algorithms and trade-offs. `docs/DEMO_GUIDE.md` provides a live demonstration outline. `docs/IMPLEMENTATION_STATUS.md` lists remaining human activities. `docs/VERIFICATION.md` records testing. Original Session 1 notes are historical; this README describes the current implementation.
