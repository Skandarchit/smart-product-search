"""Eight explicit IF–THEN rules; highest-priority applicable rule wins."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

@dataclass(frozen=True)
class Rule:
    name: str
    priority: int
    percent: int
    condition: object
    explanation: str

RULES = [
 Rule('Large cart',100,15,lambda c:c['total']>=10000,'Cart total >= 10000'),
 Rule('Electronics',90,10,lambda c:c['total']>1000 and 'Electronics' in c['categories'],'Total > 1000 and Electronics'),
 Rule('Loyal customer',80,8,lambda c:c['loyal'],'Loyal customer flag'),
 Rule('New customer',70,5,lambda c:c['new'],'New customer flag'),
 Rule('Bulk purchase',60,7,lambda c:c['quantity']>=5,'At least five units'),
 Rule('Home selection',50,6,lambda c:'Home' in c['categories'] and c['total']>=500,'Home category and total >= 500'),
 Rule('Fashion selection',40,5,lambda c:'Fashion' in c['categories'] and c['total']>=1000,'Fashion category and total >= 1000'),
 Rule('SAVE5 coupon',30,5,lambda c:c['coupon']=='SAVE5','Coupon matches SAVE5'),
]

def evaluate(cart,new=False,loyal=False,coupon=''):
    if new and loyal: raise ValueError('Choose new or loyal, not both')
    currencies = {p.currency for p,q in cart}
    if len(currencies)>1: raise ValueError('A cart cannot mix currencies')
    if any(not isinstance(q,int) or isinstance(q,bool) or q<1 for p,q in cart): raise ValueError('Quantities must be positive integers')
    total = sum((p.price*q for p,q in cart),Decimal('0'))
    context = dict(total=total,quantity=sum(q for p,q in cart),categories={p.category[0] for p,q in cart},new=new,loyal=loyal,coupon=coupon.strip().upper())
    matches = sorted([r for r in RULES if total>0 and r.condition(context)],key=lambda r:-r.priority)
    discount = (total*Decimal(matches[0].percent)/100).quantize(Decimal('.01'),rounding=ROUND_HALF_UP) if matches else Decimal('0')
    return {'total':str(total),'currency':next(iter(currencies),'INR'),'applicable':[{'name':r.name,'priority':r.priority,'percent':r.percent,'why':r.explanation} for r in matches],
            'applied':matches[0].name if matches else None,'discount':str(discount),'payable':str(total-discount),'policy':'Highest priority only; no stacking'}
