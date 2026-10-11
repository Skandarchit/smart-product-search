"""Pandas/NumPy analytics; source data and synthetic teaching fields stay labeled."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).with_name('data')

def load_clean(path=None):
    df = pd.read_csv(path or DATA/'retail_products.csv',dtype={'product_id':str})
    required = {'product_id','name','price','category','rating'}
    if not required.issubset(df.columns): raise ValueError('Product CSV is missing required columns')
    audit = {'input_rows':len(df),'input_shape':list(df.shape),'dtypes':df.dtypes.astype(str).to_dict(),'missing_before':df.isna().sum().to_dict()}
    for col in ('price','rating'): df[col] = pd.to_numeric(df[col],errors='coerce')
    df = df.dropna(subset=['product_id','name','price']).copy()
    df = df[np.isfinite(df.price) & (df.price>=0)]
    df = df[df.name.astype(str).str.strip().ne('') & df.product_id.astype(str).str.strip().ne('')]
    df['category'] = df.category.fillna('Other > General > Gifts')
    df.loc[~np.isfinite(df.rating) | ~df.rating.between(0,5),'rating'] = np.nan
    df = df.drop_duplicates('product_id',keep='last')
    audit['clean_rows'] = len(df); audit['dropped_rows'] = audit['input_rows']-len(df)
    audit['missing_after'] = df.isna().sum().to_dict()
    return df,audit


def filter_products(df,low=0,high=float('inf'),category=None,minimum_rating=0,sort_by='price'):
    if low<0 or high<low or not 0<=minimum_rating<=5: raise ValueError('Invalid filter bounds')
    if sort_by not in ('price','rating'): raise ValueError('Sort by price or rating')
    mask = df.price.between(low,high) & df.rating.ge(minimum_rating)
    if category: mask &= df.category.eq(category)
    return df[mask].sort_values(sort_by,ascending=(sort_by=='price'))


def summarize(df):
    overall = df[['price','rating']].agg(['mean','median','std','min','max'])
    grouped = df.groupby('category')[['price','rating']].agg(['mean','median','std','min','max'])
    return overall,grouped


def sales_summary(products,path=None):
    sales = pd.read_csv(path or DATA/'retail_sales.csv',dtype={'product_id':str,'invoice_id':str})
    sales['date'] = pd.to_datetime(sales.date,errors='coerce')
    for col in ('quantity','unit_price'): sales[col] = pd.to_numeric(sales[col],errors='coerce')
    sales = sales.dropna(subset=['date','quantity','unit_price'])
    sales = sales[np.isfinite(sales.quantity)&np.isfinite(sales.unit_price)&(sales.quantity>0)&(sales.unit_price>0)]
    sales = sales.merge(products[['product_id','category']],on='product_id',how='inner',validate='many_to_one')
    sales['revenue'] = sales.quantity*sales.unit_price
    sales['month'] = sales.date.dt.to_period('M').astype(str)
    monthly = sales.groupby(['category','month']).revenue.sum().reset_index()
    categories = sales.groupby('category').revenue.sum().nlargest(3)
    orders = sales.groupby('product_id').invoice_id.nunique().nlargest(5)
    return monthly,categories,orders


def export_report(output='reports'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import json
    out = Path(output); out.mkdir(parents=True,exist_ok=True)
    df,audit = load_clean(); overall,grouped = summarize(df)
    monthly,categories,orders = sales_summary(df)
    overall.to_csv(out/'statistics.csv'); grouped.to_csv(out/'category_statistics.csv')
    monthly.to_csv(out/'monthly_revenue.csv',index=False); categories.to_csv(out/'top_categories.csv'); orders.to_csv(out/'top_products_orders.csv')
    (out/'cleaning_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    filter_products(df,0,20,minimum_rating=3,sort_by='price').to_csv(out/'filtered_price.csv',index=False)
    filter_products(df,0,20,minimum_rating=3,sort_by='rating').to_csv(out/'filtered_rating.csv',index=False)
    fig,ax = plt.subplots(figsize=(9,5)); categories.rename(index=lambda x:x.split(' > ')[1]).plot.bar(ax=ax,color='#237c89')
    ax.set(title='Top categories in the retained transaction subset',xlabel='Inferred category',ylabel='Sales value (GBP; positive sales only)'); ax.tick_params(axis='x',rotation=15); fig.tight_layout(); fig.savefig(out/'category_revenue.png',dpi=150); plt.close(fig)
    fig,ax = plt.subplots(figsize=(9,5)); ax.hist(df.price,bins=30,color='#237c89'); ax.set(title='Observed product price distribution',xlabel='Last retained unit price (GBP)',ylabel='Number of products'); fig.tight_layout(); fig.savefig(out/'price_histogram.png',dpi=150); plt.close(fig)
    fig,ax = plt.subplots(figsize=(9,5)); ax.scatter(df.price,df.rating,s=12,alpha=.5); ax.set(title='Teaching ratings versus observed prices',xlabel='Last retained unit price (GBP)',ylabel='Synthetic rating (0–5)'); fig.tight_layout(); fig.savefig(out/'price_rating_scatter.png',dpi=150); plt.close(fig)
    interpretations = [f'The leading inferred category by retained positive sales value is {categories.index[0]}; investigate its stock needs within this subset.' if len(categories) else 'No category sales available.',
        f'The median retained product price is GBP {df.price.median():.2f}; use it to choose useful demonstration price filters.',
        'Ratings are deterministic synthetic teaching values: the scatter cannot support customer-satisfaction or pricing conclusions.']
    (out/'chart_interpretations.txt').write_text('\n'.join(interpretations),encoding='utf-8')
    return {'products':len(df),'output':str(out),'interpretations':interpretations}
