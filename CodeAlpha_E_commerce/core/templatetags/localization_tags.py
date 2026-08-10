from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='localize_price')
def localize_price(price, request):
    if price is None:
        return ''
    try:
        price_val = Decimal(str(price))
    except (ValueError, TypeError):
        return price
        
    loc = getattr(request, 'localization', None)
    if not loc:
        return f"PKR {price_val:,.0f}"
        
    rate = Decimal(loc['rate'])
    symbol = loc['symbol']
    
    converted = price_val * rate
    
    if converted % 1 == 0:
        return f"{symbol}{converted:,.0f}"
    return f"{symbol}{converted:,.2f}"
