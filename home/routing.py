from django.urls import re_path
from home.PermutacjeKartConsumer import PermutacjeKartConsumer

websocket_urlpatterns = [
    re_path(r'ws/$', PermutacjeKartConsumer.as_asgi()),
]