import urllib.request
import json
from decimal import Decimal
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

CURRENCY_SYMBOLS = {
    'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'PKR': 'Rs ',
    'AED': 'AED ', 'SAR': 'SAR ', 'CAD': 'CA$', 'AUD': 'A$', 'JPY': '¥',
    'CNY': 'CN¥', 'TRY': '₺', 'QAR': 'QR ', 'KWD': 'KD ', 'OMR': 'OMR ',
    'BHD': 'BD ', 'MYR': 'RM', 'SGD': 'S$', 'ZAR': 'R '
}

COUNTRY_LANGUAGES = {
    'FR': 'fr',
    'DE': 'de',
    'IT': 'it',
    'ES': 'es',
    'JP': 'ja',
    'CN': 'zh-hans',
    'PK': 'en',
    'IN': 'en',
    'US': 'en',
    'GB': 'en',
    'AE': 'en',
    'SA': 'en',
}

def get_exchange_rates():
    rates = cache.get('exchange_rates')
    if rates:
        return rates
        
    try:
        url = "https://open.er-api.com/v6/latest/PKR"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get('result') == 'success':
                rates = data['rates']
                cache.set('exchange_rates', rates, 3600 * 12) # Cache for 12 hours
                return rates
    except Exception as e:
        logger.error(f"Failed to fetch exchange rates: {e}")
        
    # Fallback rates
    return {
        'PKR': 1.0, 'USD': 0.0036, 'EUR': 0.0033, 'GBP': 0.0028, 'INR': 0.30,
        'AED': 0.0133, 'SAR': 0.0135, 'CAD': 0.0049, 'AUD': 0.0055, 'JPY': 0.55,
        'CNY': 0.026, 'TRY': 0.12, 'QAR': 0.013, 'KWD': 0.0011, 'OMR': 0.0014,
        'BHD': 0.0014, 'MYR': 0.017, 'SGD': 0.0048, 'ZAR': 0.068
    }

def get_browser_locale(request):
    accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if accept_lang:
        langs = [lang.split(';')[0].strip() for lang in accept_lang.split(',')]
        if langs:
            primary = langs[0].split('-')
            if len(primary) == 2:
                lang = primary[0].lower()
                country = primary[1].upper()
                return {'country': country, 'lang': lang}
    return None

def detect_user_location(ip: str, request):
    # Default fallback
    loc_data = {
        'country': 'US',
        'timezone': 'America/New_York',
        'currency': 'USD',
        'language': 'en'
    }
    
    # Try IP detection
    if ip and ip not in ('127.0.0.1', 'localhost', '::1'):
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,timezone,currency"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                if data.get('status') == 'success':
                    loc_data['country'] = data.get('countryCode', 'US')
                    loc_data['timezone'] = data.get('timezone', 'America/New_York')
                    loc_data['currency'] = data.get('currency', 'USD')
                    loc_data['language'] = COUNTRY_LANGUAGES.get(loc_data['country'], 'en')
                    return loc_data
        except Exception:
            pass
            
    # Try browser locale
    locale = get_browser_locale(request)
    if locale:
        loc_data['country'] = locale['country']
        loc_data['language'] = COUNTRY_LANGUAGES.get(locale['country'], locale['lang'])
        return loc_data
        
    return loc_data

def get_localization_info(request):
    if 'localization' in request.session:
        return request.session['localization']
        
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    loc = detect_user_location(ip, request)
    rates = get_exchange_rates()
    
    currency = loc['currency']
    if currency not in rates:
        currency = 'USD' # Fallback
        
    rate = rates.get(currency, 1.0)
    symbol = CURRENCY_SYMBOLS.get(currency, currency + ' ')
    
    loc['rate'] = str(rate)
    loc['symbol'] = symbol
    loc['currency'] = currency
    
    request.session['localization'] = loc
    return loc
