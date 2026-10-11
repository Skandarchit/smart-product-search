"""Run python main.py --help for all options."""
import argparse
import json
from smart_search.catalog import load_sample
from smart_search.models import money
from smart_search.categories import diagram
from smart_search.benchmark import compare


def main():
    parser = argparse.ArgumentParser(description="Smart Product Search: Session 1")
    parser.add_argument("--name", help="Case-insensitive name substring")
    parser.add_argument("--price", type=money, help="Exact price, up to two decimals")
    parser.add_argument("--category", help="Category prefix separated with >")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--dataset", choices=["session1","teaching","retail"], default="session1")
    parser.add_argument("--experiments", action="store_true")
    parser.add_argument("--analytics", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.experiments:
        from smart_search.experiments import run
        print(json.dumps(run(),indent=2)); return
    if args.analytics:
        from smart_search.analytics import export_report
        print(json.dumps(export_report(),indent=2)); return
    if args.demo:
        from smart_search.service import SearchEngine
        engine = SearchEngine("retail" if args.dataset=="retail" else "teaching")
        first = next(iter(engine.catalog.by_id))
        print(json.dumps({"catalog_size":len(engine.catalog.by_id), "search":[p.row() for p in engine.search("bag" if args.dataset=="retail" else "phone")][:5], "recommendations":engine.recommend(next(iter(engine.graph.adj),"u:NEW")), "ranking":engine.rank(budget=5 if args.dataset=="retail" else 2500)["results"], "cart":engine.checkout({first:2},new=True,coupon="SAVE5")},indent=2)); return
    from smart_search.catalog import load_extended, load_retail
    catalog = {"session1":load_sample,"teaching":load_extended,"retail":load_retail}[args.dataset]()
    if args.benchmark:
        print(json.dumps(compare(catalog, [2499, 99, 45999, 100]), indent=2))
    elif args.price is not None:
        print(json.dumps([p.row() for p in catalog.prices.search_price(args.price)], indent=2))
    elif args.name is not None or args.category is not None:
        category = tuple(c.strip() for c in args.category.split(">")) if args.category else None
        print(json.dumps([p.row() for p in catalog.browse(args.name or "", category)], indent=2))
    else:
        print("PRODUCTS IN ASCENDING PRICE ORDER")
        for product in catalog.prices.inorder():
            print(product.row())
        print("\nTHREE-LEVEL CATEGORIES\n" + diagram(catalog.linked.traverse()))


if __name__ == "__main__":
    main()
