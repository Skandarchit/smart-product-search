"""Repeated exact-price queries on the same records, excluding construction."""
from statistics import median
from time import perf_counter_ns
from .models import money


def compare(catalog, queries, repeats=1000, rounds=7):
    queries = [money(q) for q in queries]
    if not queries or repeats < 1 or rounds < 1:
        raise ValueError("Need queries and positive repeats/rounds")
    methods = {"linked_list": catalog.linked.search_price,
               "bst": catalog.prices.search_price}
    for query in queries:
        if methods["linked_list"](query) != methods["bst"](query):
            raise AssertionError("Indexes disagree")
    # Warm both implementations before timing. Alternate order across rounds.
    for method in methods.values():
        for query in queries:
            method(query)
    samples = {name: [] for name in methods}
    for round_number in range(rounds):
        order = list(methods) if round_number % 2 == 0 else list(reversed(methods))
        for name in order:
            start = perf_counter_ns()
            for _ in range(repeats):
                for query in queries:
                    methods[name](query)
            elapsed = perf_counter_ns() - start
            samples[name].append(elapsed / (repeats * len(queries)))
    return {"products": len(list(catalog.linked.traverse())),
            "queries": [str(q) for q in queries], "repeats": repeats,
            "rounds": rounds, "unit": "nanoseconds per query",
            "median_ns": {k: median(v) for k, v in samples.items()},
            "samples_ns": samples}
