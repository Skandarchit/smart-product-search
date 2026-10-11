"""Session 2: exact-name searches. Binary input must be casefold-sorted."""
def linear_search(products, name):
    target = name.strip().casefold()
    return [p for p in products if p.name.casefold() == target]


def binary_search(products, name):
    target = name.strip().casefold()
    lo, hi = 0, len(products)
    while lo < hi:
        mid = (lo + hi) // 2
        if products[mid].name.casefold() < target:
            lo = mid + 1
        else:
            hi = mid
    result = []
    while lo < len(products) and products[lo].name.casefold() == target:
        result.append(products[lo]); lo += 1
    return result
