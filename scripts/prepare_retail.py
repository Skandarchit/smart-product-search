"""Rebuild included derived CSVs from the UCI ZIP: python scripts/prepare_retail.py ZIP."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from collections import Counter,defaultdict
from decimal import Decimal,ROUND_HALF_UP
import csv,json,hashlib,sys
import openpyxl
out=Path(__file__).resolve().parents[1]/'smart_search/data'
source=Path(sys.argv[1])
with ZipFile(source) as z:
    workbook=openpyxl.load_workbook(BytesIO(z.read('Online Retail.xlsx')),read_only=True,data_only=True)
products={}; sales=[]; interactions=Counter(); audit=Counter(); retained_customers={}
for row in workbook.active.iter_rows(min_row=2,values_only=True):
    audit['source_rows']+=1
    invoice,code,name,qty,date,price,customer,country=row
    if not name or not code or qty is None or price is None or qty<=0 or price<=0 or str(invoice).upper().startswith('C') or not str(code)[0].isdigit():
        audit['excluded_invalid_return_or_non_product']+=1;continue
    code=str(code)
    if code not in products and len(products)>=1000: continue
    text=str(name).strip(); upper=text.upper()
    group='General';leaf='Gifts'
    for words,g,l in [('BAG','Accessories','Bags'),('CUP MUG PLATE BOWL','Kitchen','Tableware'),('CANDLE LIGHT LANTERN','Decor','Lighting'),('CHRISTMAS XMAS','Seasonal','Decorations'),('BOX TIN','Storage','Containers')]:
        if any(w in upper for w in words.split()): group,leaf=g,l;break
    rating=round(2.5+(int(hashlib.sha256(code.encode()).hexdigest()[:4],16)%26)/10,1)
    products[code]={'product_id':code,'name':text,'price':str(Decimal(str(price)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)),'category':f'Home > {group} > {leaf}','rating':rating,'currency':'GBP','rating_source':'synthetic teaching value','category_source':'keyword-inferred'}
    sales.append({'invoice_id':str(invoice),'product_id':code,'quantity':qty,'unit_price':price,'date':date.isoformat()})
    if customer is not None:
        token=str(customer)
        if token not in retained_customers: retained_customers[token]=f'U{len(retained_customers)+1:05}'
        interactions[(retained_customers[token],code)]+=1
workbook.close()
for file,rows in [('retail_products.csv',list(products.values())),('retail_sales.csv',sales)]:
    with (out/file).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
# Small observed graph with eight users; no fabricated links. Product count varies.
users=[u for u,n in Counter({u:sum(w for (v,p),w in interactions.items() if v==u) for u in list(retained_customers.values())[:100]}).most_common(8)]
edges=[('u:'+u,'p:'+p,w) for (u,p),w in interactions.items() if u in users]
(out/'retail_interactions.json').write_text(json.dumps(edges),encoding='utf-8')
audit.update({'retained_products':len(products),'retained_sales_lines':len(sales),'graph_users':len(users),'graph_edges':len(edges)})
(out/'retail_provenance.json').write_text(json.dumps({'source':'Chen, D. (2015). Online Retail. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33','license':'CC BY 4.0 https://creativecommons.org/licenses/by/4.0/','download':'https://archive.ics.uci.edu/static/public/352/online+retail.zip','zip_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'transformations':['First 1000 valid product stock codes in source order; all positive sales lines for those codes retained','Cancellations, non-positive prices/quantities, missing names and non-numeric-leading codes excluded','Last observed retained description and price per code; catalogue prices rounded to two decimals','Categories inferred using keyword rules, not supplied by retailer','Ratings generated deterministically for teaching, not customer feedback','Graph uses eight active users among first 100 observed users, with anonymized IDs and purchase-line-count weights','Sales use historical transaction unit prices, not current catalog prices; totals exclude returns and are not net revenue'], 'audit':dict(audit)},indent=2),encoding='utf-8')
print(dict(audit))
