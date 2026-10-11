# Data and source notes

The supplied Sessions 2–8 DOCX texts were inspected directly from Downloads. Their tasks define the implementation requirements. Extracts are in SESSION_2_8_SOURCE_EXTRACTS.json; original documents are unchanged.

## Retail dataset

Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Dataset description and download](https://archive.ics.uci.edu/dataset/352/online+retail).

The source describes historical UK transactions and sterling unit prices. This project retains the first 1,000 valid stock codes encountered and their positive sales lines, excluding cancellations and non-product rows. Category keyword rules and deterministic synthetic ratings were added for coursework fields absent from the source. Catalog prices use the last retained unit price rounded to two decimals; transaction totals use original transaction prices. The graph derives weights from retained purchase-line counts for eight anonymized users. The complete transformations, source ZIP hash and row counts are in retail_provenance.json. No original customer IDs are distributed.

Rebuild from the original downloaded ZIP with `python scripts/prepare_retail.py path/to/online-retail.zip`. The ZIP itself is not bundled; the derived CSVs are bundled with attribution.

## Three search tools: evidence versus inference

- Amazon: a 2022 Amazon Science publication discusses query/product semantic similarity as a ranking feature and evaluation signal. It demonstrates relevance-model research, not that Amazon uses this project's BST for text search. [Publication](https://www.amazon.science/publications/improving-relevance-quality-in-product-search-using-high-precision-query-product-semantic-similarity).
- Flipkart: the observed public search page exposes category/rating filters and popularity/price sorting. Indexed filtering and ranking are reasonable algorithmic interpretations of those capabilities; the backend structures cannot be inferred from the page. [Search page](https://www.flipkart.com/search/pr?sid=all).
- Google Shopping: its help page describes relevance and personalization based on searches and other activity. This supports a distinction between exact matching and contextual ranking, without identifying its internal index implementation. [Official explanation](https://support.google.com/googleshopping/answer/15456476?hl=en).

Sources accessed 2026-10-11. These observations are not benchmark comparisons among the services.

## B-tree research note

A binary tree has at most two children per node; a B-tree stores several ordered keys and child pointers in each node. Splits preserve a balanced height as keys arrive. More keys per node can reduce traversal depth and disk-page access. PostgreSQL documents its B-tree as a multi-way balanced tree and supports equality/range comparisons and ordered retrieval. An index also incurs update and storage costs. The small in-memory BTree class illustrates splitting and searching; it does not implement PostgreSQL pages, concurrency or durability. [PostgreSQL index types](https://www.postgresql.org/docs/current/indexes-types.html), [B-tree details](https://www.postgresql.org/docs/current/btree.html).
