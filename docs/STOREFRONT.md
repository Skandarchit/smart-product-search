# Shopping interface

The default page is Shop. Choose a collection, enter a product name, optionally choose a department or maximum price, and press Find products. The Home & gifts collection uses historical GBP examples; Everyday essentials uses fictional INR examples. Currencies are not converted or mixed.

Products appear as cards with a readable name, price, illustration and Add to cart button. View details offers related items from shopping history where available, otherwise other products from the same department. Generated ratings are not displayed. Symbols are illustrations rather than photos of the actual item.

My cart supports quantities and removal. Offers are applied automatically as the customer type or offer code changes. Subtotal, savings and total are shown clearly; no payment is taken. Carts persist during the browser session and remain separate for each collection.

Store overview is for the shop owner. It displays popular searches as a two-column list, rather than raw nested data. Only an explicit Find products submission increments a count. Historical sales are separate from demo cart activity.

Coursework contains the original algorithm comparisons, traces, catalog management and learning exercises. The algorithm modules remain available through the CLI. The existing technical demonstration guide can be followed inside this area.

To load the new theme, stop the running app with Ctrl+C, run python -m streamlit run app.py again from Desktop/IP project, and refresh your browser. No new dependencies are required.

Validation: the automated shopping journey passed, covering exact five-result alarm-clock search, refresh-safe search counts, related-product details, repeated additions, quantity changes, coupon totals, removal, separate collection carts, store overview and coursework. A local browser preview was visually checked.
