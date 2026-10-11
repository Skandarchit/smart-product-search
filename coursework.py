import json
from pathlib import Path
import streamlit as st
from smart_search.service import SearchEngine
from smart_search.models import Product
from smart_search.search import binary_search,linear_search
from smart_search.categories import diagram
from smart_search.heaps import top_rated,fulfill_orders
from smart_search.knowledge import semantic_network,make_frame,FRAMES



def render(engine):
    catalog=engine.catalog
    key=engine.dataset
    currency="GBP" if key=="retail" else "INR"
    page=st.selectbox("Coursework exercise",["Search","Recommendations","Cart and discounts","Analytics","Learning lab"],key="lab_page")
    def display(products): st.dataframe([p.row() for p in products],hide_index=True)
    if page=='Search':
        a,b,c=st.columns(3)
        with a: query=st.text_input('Product name',key='query')
        with b: category=st.selectbox('Category',['All']+sorted({p.category[0] for p in catalog.by_id.values()}),key='category')
        with c: mode=st.selectbox('Search method',['Contains (category index)','Exact linear','Exact binary'],key='search_mode')
        if mode=='Contains (category index)': matches=engine.search(query,(category,) if category!='All' else None)
        else:
            candidates=list(catalog.by_id.values())
            if category!='All': candidates=[p for p in candidates if p.category[0]==category]
            matches=(binary_search(sorted(candidates,key=lambda p:p.name.casefold()),query) if mode=='Exact binary' else linear_search(candidates,query))
            if query.strip():catalog.terms[query.strip().casefold()]+=1
        st.write(f'{len(matches)} products');display(matches)
        a,b=st.columns(2)
        with a:
            exact=st.text_input(f'Exact price ({currency})','2499' if key=='teaching' else '2.95',key='exact_price')
            index=st.selectbox('Price index',['AVL','BST','B-tree'],key='price_index')
            try: display({'AVL':catalog.avl,'BST':catalog.prices,'B-tree':catalog.btree}[index].search_price(exact))
            except ValueError as exc: st.error(str(exc))
        with b:
            pid=st.text_input('Lookup product ID',key='lookup_id')
            if pid: display([catalog.by_id[pid]] if pid in catalog.by_id else [])
            st.caption('Search counts are available in Store overview.')
        with st.expander('Add or delete a product'):
            with st.form('add'):
                pid=st.text_input('Unique ID',key='pid');name=st.text_input('Name',key='new_name');price=st.text_input('Price','0.00',key='new_price')
                path=st.text_input('Three category levels separated by >','Electronics > Mobiles > Smartphones',key='new_category')
                rating=st.number_input('Teaching rating',0.0,5.0,4.0,key='new_rating')
                if st.form_submit_button('Add product',key='add_product'):
                    try: engine.add(Product(pid,name,price,tuple(path.split('>')),rating,currency));st.success('Added. Search again to refresh results.')
                    except ValueError as exc:st.error(str(exc))
            with st.form('delete'):
                pid=st.text_input('ID to delete',key='delete_id')
                if st.form_submit_button('Delete product',key='delete_product'):
                    st.success('Deleted. Indexes and graph updated.') if engine.delete(pid.strip()) else st.warning('ID not found')
    elif page=='Recommendations':
        st.subheader('Graph recommendations')
        nodes=sorted(engine.graph.adj)
        start=st.selectbox('Starting product or user',nodes or ['u:NEW'],key='graph_start')
        st.dataframe(engine.recommend(start),hide_index=True)
        with st.expander('Traversal traces'):
            st.json({'BFS':engine.graph.bfs(start,2),'DFS':engine.graph.dfs(start)})
        st.subheader('Heuristic search')
        budget=st.number_input(f'Target budget ({currency})',min_value=0.01,value=2500.0 if key=='teaching' else 5.0,key='budget')
        preference=st.selectbox('Preferred category',['Any']+sorted({p.category[0] for p in catalog.by_id.values()}),key='preference')
        if st.button('Compare BFS, greedy and A*',key='rank'):
            for method in ('bfs','greedy','astar'):
                report=engine.rank(method,budget,None if preference=='Any' else preference)
                st.write(f'{method}: {report["expanded"]} nodes expanded');st.dataframe(report['results'])
                with st.expander(method+' trace'):st.json(report['trace'])
        st.caption('The heuristic uses price, rating and category. It scores the catalog first; node counts exclude this preprocessing. Ratings are teaching data.')
    elif page=='Cart and discounts':
        ids=st.multiselect('Products',list(catalog.by_id),format_func=lambda pid:f'{pid}: {catalog.by_id[pid].name}',key='cart_ids')
        quantities={pid:int(st.number_input('Quantity: '+pid,min_value=1,max_value=100,value=1,key='qty_'+pid)) for pid in ids}
        profile=st.selectbox('Customer',['Returning','New','Loyal'],key='profile');coupon=st.text_input('Coupon',key='coupon')
        if st.button('Evaluate discounts',key='checkout'):
            st.json(engine.checkout(quantities,new=profile=='New',loyal=profile=='Loyal',coupon=coupon))
        st.caption('Eight teaching rules. All matches appear in priority order; only the highest-priority rule applies. Thresholds are illustrative in the selected currency.')
    elif page=='Analytics':
        from smart_search.analytics import load_clean,filter_products,summarize,sales_summary,export_report
        st.info('Analytics uses the bundled historical UCI CSV snapshot; it does not include in-memory catalog edits. Ratings are synthetic; categories are inferred.')
        df,audit=load_clean();st.json(audit)
        high=st.number_input('Maximum price (GBP)',min_value=0.0,value=20.0,key='max_price');rating=st.slider('Minimum teaching rating',0.0,5.0,3.0)
        selected=st.selectbox('Analytics category',['All']+sorted(df.category.unique()),key='analytics_category')
        order=st.selectbox('Sort results by',['price','rating'],key='analytics_sort')
        st.dataframe(filter_products(df,0,high,None if selected=='All' else selected,rating,order),hide_index=True)
        overall,grouped=summarize(df);st.subheader('Price and rating statistics');st.dataframe(overall);st.dataframe(grouped)
        monthly,top,orders=sales_summary(df);st.subheader('Historical positive sales');st.dataframe(monthly);st.bar_chart(top);st.write('Top five products by distinct order count');st.dataframe(orders)
        if st.button('Generate analytics files',key='analytics_export'):st.json(export_report())
        for filename in ('category_revenue.png','price_histogram.png','price_rating_scatter.png'):
            path=Path('reports')/filename
            if path.exists():st.image(str(path))
    else:
        st.subheader('Data structures')
        st.code(' -> '.join(p.product_id for p in list(catalog.linked.traverse())[:20])+' -> ...')
        st.code(diagram(catalog.linked.traverse()));display(catalog.avl.inorder())
        st.subheader('Max-heap rating order');display(top_rated(catalog.by_id.values(),15))
        orders=json.loads((Path(__file__).parent/'smart_search/data/orders.json').read_text());st.write('Deadline queue');st.json(fulfill_orders(orders))
        kind=st.selectbox('Frame example',list(FRAMES));st.json(make_frame(kind));st.write('Synthetic semantic-network teaching triples');st.dataframe(semantic_network(catalog.by_id.values()))
        st.caption('Run python main.py --experiments to regenerate heap steps, hash collisions, tree comparisons and search traces.')
        if st.button('Run experiments',key='experiments'):
            from smart_search.experiments import run
            st.json(run())
        report=Path('reports/session_experiments.json')
        if report.exists():
            with st.expander('Experiment results'):st.json(json.loads(report.read_text()))
