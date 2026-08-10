from core.localization import get_localization_info
import contextvars
from django.utils import timezone, translation

current_request = contextvars.ContextVar('current_request', default=None)

class LocalizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        loc = get_localization_info(request)
        request.localization = loc
        
        # Set timezone
        if loc.get('timezone'):
            try:
                timezone.activate(loc['timezone'])
            except Exception:
                timezone.activate('America/New_York')
                
        # Set language
        if loc.get('language'):
            translation.activate(loc['language'])
            request.LANGUAGE_CODE = loc['language']
            
        token = current_request.set(request)
        try:
            response = self.get_response(request)
            return response
        finally:
            current_request.reset(token)
            timezone.deactivate()
            translation.deactivate()
