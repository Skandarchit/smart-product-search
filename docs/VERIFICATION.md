# Verification

Verified on 2026-10-11 with Python 3.12, Streamlit 1.65.0, Pandas 3.0.6 and NumPy 2.5.4 on Windows.

All 38 tests passed in 19.024 seconds with no skips: 14 original core tests, 8 additional algorithm tests, 15 integration tests and one multi-page Streamlit AppTest flow. The UI test covered name search, insertion/deletion, invalid prices, recommendations, heuristic comparison, cart rules, analytics, the learning lab, switching to the real-data catalog and reset. AppTest verifies widget behavior and execution, not browser visual layout.

The complete suite passed outside the restricted sandbox; its temporary-file permissions prevented one fixture test and stalled Streamlit inside the sandbox. No application defect was inferred from those sandbox restrictions.

The real-data CLI demo completed. Experiment and analytics commands completed and generated their bundled reports. The one-page poster and four chart images were visually inspected. The source dataset processor retained 1000 products and 275602 transaction lines from 541909 source rows. Local timings are illustrative and can vary on another computer.

## Storefront redesign

The replacement Streamlit shopping journey test passed on 2026-10-11 (13.109 seconds). It verifies search submission counts, five alarm-clock results, product details, cart additions/quantities/removal, offers, collection switching, store overview and coursework access. The prior 37 core/algorithm/integration cases were unchanged. The light storefront and product cards were checked in a local browser.
