from django.urls import re_path
from home.consumers import TestConsumer

websocket_urlpatterns = [
    re_path(r'ws/progress/', TestConsumer.as_asgi()),
]