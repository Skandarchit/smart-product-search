"""A simple storefront, with course demonstrations in a separate area."""
from pathlib import Path
from decimal import Decimal
from html import escape
import streamlit as st
from smart_search.service import SearchEngine
from smart_search.storefront import browse,title,price,related

st.set_page_config(page_title='Find & Co. | Product discovery',page_icon='🛍️',layout='wide')
st.markdown("""<style>
.block-container {max-width:1200px;padding-top:2rem;padding-bottom:3rem;}
[data-testid="stSidebar"] {background:#f0eee8;}
.shop-brand {font-size:27px;font-weight:800;letter-spacing:-1px;color:#23463c;margin-bottom:3px;}
.shop-eyebrow {font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#577569;font-weight:700;}
.shop-hero {background:#e6eee5;border-radius:20px;padding:18px 26px;margin:0 0 18px;}
.shop-hero h1 {font-size:30px;line-height:1.1;color:#173e31;margin:9px 0 13px;letter-spacing:-1px;}
.shop-hero p {font-size:16px;color:#486154;margin:0;}
.product-art {height:105px;background:#f2eee5;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:48px;margin-bottom:12px;}
.product-dept {font-size:11px;letter-spacing:1.1px;text-transform:uppercase;color:#68746b;}
.product-title {font-size:16px;line-height:1.4;font-weight:600;color:#253b31;min-height:48px;margin:7px 0;}
.product-price {font-size:23px;font-weight:750;color:#214b39;margin:6px 0 15px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px;}
button {border-radius:9px!important;}
</style>""",unsafe_allow_html=True)
st.sidebar.markdown('<div class="shop-brand">Find & Co.</div>',unsafe_allow_html=True)
st.sidebar.caption('Find a product. Make it yours.')
collection=st.sidebar.selectbox('Browse a collection',['Home & gifts · £','Everyday essentials · ₹'],key='shop_collection')
dataset='retail' if collection.startswith('Home') else 'teaching'
if 'shop_engine' not in st.session_state or st.session_state.shop_engine.dataset!=dataset:
    st.session_state.shop_engine=SearchEngine(dataset)
engine=st.session_state.shop_engine;catalog=engine.catalog
currency='GBP' if dataset=='retail' else 'INR'
if 'shopping_carts' not in st.session_state:st.session_state.shopping_carts={}
cart=st.session_state.shopping_carts.setdefault(dataset,{})
# A product removed from the manager cannot stay in the customer cart.
for pid in list(cart):
    if pid not in catalog.by_id:cart.pop(pid)
page=st.sidebar.radio('Go to',['Shop','My cart','Store overview','Coursework'],key='shop_page')
st.sidebar.divider()
st.sidebar.write(f'🛍️ {sum(cart.values())} items in your cart')
st.sidebar.caption('Shopping demo • no payments or orders')
with st.sidebar.expander('About this collection'):
    st.write('Historical home and gift products, priced in British pounds. Prices are examples, not live offers.' if dataset=='retail' else 'Sample electronics, clothing and everyday products, priced in Indian rupees.')
    st.caption('Product symbols are illustrations, not photos. Category labels are added for browsing. Generated ratings are not shown in the shop.')
    st.caption('Your cart stays during this browser session. Each collection has its own cart.')
notice=st.session_state.pop('shop_notice',None)
if notice:st.success(notice)


def icon(p):
    name=p.name.casefold()
    for words,symbol in [('clock','⏰'),('phone','📱'),('laptop computer','💻'),('headphone speaker','🎧'),('bag','🛍️'),('mug cup bowl plate','☕'),('shoe','👟'),('shirt','👕'),('lamp candle light','💡'),('bottle','🧴'),('notebook','📓'),('pan','🍳'),('box tin','🎁')]:
        if any(w in name for w in words.split()):return symbol
    return '🎁'


def add(pid):
    cart[pid]=cart.get(pid,0)+1
    st.session_state['quantity_'+dataset+'_'+pid]=cart[pid]
    st.session_state['shop_notice']='Added '+title(catalog.by_id[pid])+' to your cart.'


def set_quantity(pid,key):
    cart[pid]=int(st.session_state[key])


def cards(products,prefix):
    for offset in range(0,len(products),3):
        columns=st.columns(3)
        for column,p in zip(columns,products[offset:offset+3]):
            with column,st.container(border=True):
                st.markdown(f'<div class="product-art">{icon(p)}</div><div class="product-dept">{escape(p.category[1])}</div><div class="product-title">{escape(title(p))}</div><div class="product-price">{price(p.price,p.currency)}</div>',unsafe_allow_html=True)
                left,right=st.columns(2)
                left.button('Add to cart',key=prefix+'_add_'+p.product_id,on_click=add,args=(p.product_id,),type='primary',use_container_width=True)
                if right.button('View details',key=prefix+'_view_'+p.product_id,use_container_width=True):
                    st.session_state['selected_'+dataset]=p.product_id;st.rerun()


if page=='Shop':
    st.markdown('<div class="shop-hero"><div class="shop-eyebrow">A simpler way to shop</div><h1>'+('A little something for your home.' if dataset=='retail' else 'Everyday finds, all in one place.')+'</h1><p>Search for what you need, choose a budget, and explore your favourites.</p></div>',unsafe_allow_html=True)
    with st.form('shop_search'):
        query=st.text_input('What are you looking for?',placeholder='Try alarm clock, mug or bag' if dataset=='retail' else 'Try phone, headphones or shoes',key='shop_query_'+dataset)
        a,b,c=st.columns([1.2,1,1.2])
        department=a.selectbox('Department',['All departments']+sorted({p.category[1] for p in catalog.by_id.values()}),key='shop_department_'+dataset)
        budget=b.number_input('Maximum price ('+('£' if dataset=='retail' else '₹')+') · 0 means any',min_value=0.0,value=0.0,step=5.0 if dataset=='retail' else 500.0,key='shop_budget_'+dataset)
        order=c.selectbox('Sort by',['Featured','Price: low to high','Price: high to low','Name: A to Z'],key='shop_order_'+dataset)
        submitted=st.form_submit_button('Find products',type='primary',use_container_width=True,key='find_products')
    if submitted:
        if query.strip():catalog.terms[query.strip().casefold()]+=1
        st.session_state['shop_paging_'+dataset]=1
        st.session_state.pop('selected_'+dataset,None)
    selected=st.session_state.get('selected_'+dataset)
    if selected in catalog.by_id:
        p=catalog.by_id[selected]
        with st.container(border=True):
            st.subheader(title(p));st.write(p.category[1]+' · '+p.category[2]);st.markdown('### '+price(p.price,p.currency))
            st.button('Add this product to cart',key='detail_add',on_click=add,args=(p.product_id,),type='primary')
            if st.button('Close details',key='close_details'):
                st.session_state.pop('selected_'+dataset,None);st.rerun()
            suggestions,reason=related(engine,p)
            if suggestions:
                st.subheader('You might also like');st.caption(reason);cards(suggestions,'related')
    matches=browse(catalog.by_id.values(),query,department,Decimal(str(budget)) if budget else None,order)
    st.subheader((f'Results for “{query.strip()}”' if query.strip() else 'Explore the collection'))
    st.caption(f'{len(matches):,} products'+(' • within your budget' if budget else ''))
    if not matches:
        st.info('No products found. Try fewer words, a different department, or a higher budget.')
    else:
        pages=max(1,(len(matches)+11)//12)
        paging='shop_paging_'+dataset
        if st.session_state.get(paging,1)>pages:st.session_state[paging]=1
        current=int(st.session_state.get(paging,1))
        st.caption(f'Showing {(current-1)*12+1}–{min(current*12,len(matches))} of {len(matches):,}')
        cards(matches[(current-1)*12:current*12],'shop')
        if pages>1:st.number_input('Page',min_value=1,max_value=pages,step=1,key=paging)
elif page=='My cart':
    st.title('Your cart');st.caption('Review your choices and try the available offers. This demo does not place an order.')
    if not cart:st.info('Your cart is empty. Open Shop and choose “Add to cart” on a product you like.')
    else:
        for pid in list(cart):
            p=catalog.by_id[pid]
            with st.container(border=True):
                a,b,c=st.columns([3,1,1])
                a.markdown('**'+title(p)+'**');a.caption(price(p.price,p.currency)+' each')
                qtykey='quantity_'+dataset+'_'+pid
                st.session_state[qtykey]=cart[pid]
                b.number_input('Quantity',min_value=1,max_value=max(100,cart[pid]),step=1,key=qtykey,on_change=set_quantity,args=(pid,qtykey))
                c.write(price(p.price*cart[pid],p.currency))
                if c.button('Remove',key='remove_'+pid):
                    cart.pop(pid);st.session_state.pop(qtykey,None);st.rerun()
        st.subheader('Offers and total')
        a,b=st.columns(2)
        customer=a.selectbox('Shopping with us',['Returning customer','First visit','Loyal customer'],key='customer_type')
        coupon=b.text_input('Offer code',placeholder='Try SAVE5',key='offer_code')
        result=engine.checkout(cart,new=customer=='First visit',loyal=customer=='Loyal customer',coupon=coupon)
        a,b,c=st.columns(3);a.metric('Subtotal',price(result['total'],currency));b.metric('You save',price(result['discount'],currency));c.metric('Total',price(result['payable'],currency))
        if result['applied']:st.success('Offer applied: '+result['applied'])
        else:st.caption('No offer applies to this cart yet.')
        if coupon.strip() and coupon.strip().upper()!='SAVE5':st.warning('That offer code was not recognised.')
        with st.expander('How your offer was chosen'):
            st.write('One offer is used at a time. The first eligible offer in the store’s offer order applies.')
            for rule in result['applicable']:st.write(f"{rule['name']}: {rule['percent']}% off")
        st.caption('Demo total only. No payment will be taken.')
elif page=='Store overview':
    st.title('Store overview');st.caption('For the store owner • a simple view of product interest and historical sales.')
    st.subheader('Popular searches in this session')
    terms=catalog.terms.most_common(5)
    if terms:st.dataframe([{'Search':q,'Times searched':n} for q,n in terms],hide_index=True,use_container_width=True)
    else:st.info('Searches will appear here after someone uses “Find products”.')
    st.caption('Counted when a search is submitted, not when a page refreshes.')
    from smart_search.analytics import load_clean,sales_summary
    df,_=load_clean();monthly,categories,orders=sales_summary(df)
    st.subheader('Home & gifts sales snapshot');st.caption('Historical UK retail sales • GBP • positive sales only, excluding returns. This snapshot does not include demo cart activity.')
    a,b=st.columns(2);a.metric('Products in the snapshot',f'{len(df):,}');b.metric('Recorded sales value',price(monthly.revenue.sum(),'GBP'))
    st.write('**Top departments by sales**');st.bar_chart(categories.rename(index=lambda s:s.split(' > ')[1]))
    names=dict(zip(df.product_id.astype(str),df.name))
    st.write('**Most ordered products**');st.dataframe([{'Product':str(names.get(str(pid),pid)).title(),'Orders':int(count)} for pid,count in orders.items()],hide_index=True,use_container_width=True)
else:
    st.title('Coursework');st.caption('The algorithms and exercises behind the shop. These controls are for the project demonstration.')
    from coursework import render
    counts=catalog.terms.copy()
    render(engine)
    catalog.terms=counts
