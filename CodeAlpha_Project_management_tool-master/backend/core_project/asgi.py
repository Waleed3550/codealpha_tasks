import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator


# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')

# Initialize Django ASGI application early to ensure AppRegistry is populated
django_asgi_app = get_asgi_application()

import apps.tasks.routing
from core.middleware import JWTAuthMiddleware
import apps.chat.routing

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket handler utilizing Django Channels
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                apps.tasks.routing.websocket_urlpatterns +
                apps.chat.routing.websocket_urlpatterns
            )
        )
    ),
})
