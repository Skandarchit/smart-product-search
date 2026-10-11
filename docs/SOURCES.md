> Historical Session 1 reference. For current scope, costs and status, read README.md and IMPLEMENTATION_STATUS.md.

# Source inspection and scope

Inspected the text of ten attached DOCX files retrieved from the referenced “Generate Poster” conversation (ID 6acb273d-e920-83ec-bfbd-28012861afd7). This includes three versions of Session 1 and one each of Sessions 2–8. Paragraph and table-cell text was read from word/document.xml. No claim is made to have inspected embedded images or verified page layouts. Session 1 paragraph text is identical across its three copies (verified separately from binary file hashes).

## Traceability

Session 1, Student Task 4 directly grounds `linked_list.py`, `bst.py`, the 12-record dataset, and `benchmark.py`: at least ten name/price/category records, insertion/deletion/traversal, a BST on the same data and a timer comparison. Price indexing and duplicate-price semantics follow the user's request and the document's description. Task 5 grounds `categories.py` and the guide's three-level diagram and traversal explanation. Tasks 2–3 and Session Output inform the educational guide. Task 1's real-platform investigation has not been performed; no proprietary platform claims are made.

Sessions 2–8 are inspected planning inputs, not completed implementations. `ROADMAP.md` follows their Student Tasks. UI, stable IDs, validation, decimal money, CLI and automated tests are engineering additions. Sample records, timings and code are not attributed to the DOCX author.

## Source inconsistencies retained as caveats

Session 2 describes building on BST concepts “from Session 2” although Session 1 introduces the BST. Its Session Output also includes heap deliverables whose detailed tasks occur in Session 3. Session 5 refers to a priority queue “from Session 5” and BFS “Session 6,” while the supplied heap/graph material occurs in Session 3. Its Student Tasks include A*, although the Code Output summary emphasizes greedy search and rule evaluation. The roadmap uses the main session headings and task bodies, preserves A* as planned, and does not silently certify these cross-references as correct. B-tree research is assigned; implementation is an optional project extension.

## Inspected source identifiers

- `DOE-1 Sessions 4 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `d2cb415f573201146d331d2451fd56127b1e33118ac093f0dde5aef37d35fd99`
- `DOE-1 Sessions 7 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `d16c0c251c9286edea0f41b2838d485c68993abe6bef810be6a9766db2187f09`
- `DOE-1 Sessions 3 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `c54fd95366cec1e9ab4b16aba9e5b79541afcd5c708da58d3d7ad0ce00265de6`
- `DOE-1 Sessions 8 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `99c090c1c38e71d3875fd727316765faaca9e5a71ad04ea815b3c9000486a207`
- `DOE-1 Sessions 1 - E-Commerce Data Organization and Retrival(2).docx` — SHA-256 `cfb4735fae2f7bc36c643320ec5a34d886819db4ea0ad5a9b2a171faa3ffc93b`
- `DOE-1 Sessions 5 - E-Commerce Data Organization and Retrival (1)(1).docx` — SHA-256 `3a86b6362cb7d83da4ee3167e27757f0e55dd901080804e01540a929077b6257`
- `DOE-1 Sessions 2 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `d733b8be66b9bcb6b3d0c4f6a8cf3d664073659827a508171d313ec2b2d78b38`
- `DOE-1 Sessions 1 - E-Commerce Data Organization and Retrival.docx` — SHA-256 `cfb4735fae2f7bc36c643320ec5a34d886819db4ea0ad5a9b2a171faa3ffc93b`
- `DOE-1 Sessions 1 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `cfb4735fae2f7bc36c643320ec5a34d886819db4ea0ad5a9b2a171faa3ffc93b`
- `DOE-1 Sessions 6 - E-Commerce Data Organization and Retrival(1).docx` — SHA-256 `63a6d1048aba7e7116a5d88c2565201476f3f9c8b517fc9ce643593a968fe1bb`

The accompanying SOURCE_EXTRACTS.json contains the extracted source text, filenames and hashes. Original attachments are not modified.
