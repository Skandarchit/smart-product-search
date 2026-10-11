"""Customer-facing presentation helpers; no synthetic ratings in the shop."""

def title(product):
    return product.name.title() if product.name.isupper() else product.name


def price(value,currency):
    return ('£' if currency=='GBP' else '₹')+f'{float(value):,.2f}'


def browse(products,query='',category='All departments',budget=None,order='Featured'):
    words=query.strip().casefold().split()
    rows=[p for p in products if all(w in p.name.casefold() for w in words)
          and (category=='All departments' or p.category[1]==category)
          and (budget is None or p.price<=budget)]
    if order=='Price: low to high':rows.sort(key=lambda p:(p.price,p.name))
    elif order=='Price: high to low':rows.sort(key=lambda p:(-p.price,p.name))
    elif order=='Name: A to Z':rows.sort(key=lambda p:p.name.casefold())
    return rows


def related(engine,product,limit=3):
    # Prefer observed graph connections; otherwise make a clearly labeled
    # same-department suggestion without using invented customer ratings.
    node='p:'+product.product_id
    if node in engine.graph.adj:
        rows=engine.graph.recommend(node,limit)
        picks=[engine.catalog.by_id[x['product_id']] for x in rows if x['product_id'] in engine.catalog.by_id]
        if picks:return picks,'Related through shopping history' if engine.dataset=='retail' else 'Related in our sample collection'
    picks=[p for p in engine.catalog.by_id.values() if p.product_id!=product.product_id and p.category[:2]==product.category[:2]]
    picks.sort(key=lambda p:(abs(p.price-product.price),p.name))
    return picks[:limit],'More in '+product.category[1]
