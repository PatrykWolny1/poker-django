from django.urls import re_path
from home.CardsPermutationsConsumer import CardsPermutationsConsumer
from home.GameOnePairConsumer import GameOnePairConsumer

websocket_urlpatterns = [
    re_path('ws/perms_combs/', CardsPermutationsConsumer.as_asgi()),
    re_path('ws/op_game/', GameOnePairConsumer.as_asgi()),
]