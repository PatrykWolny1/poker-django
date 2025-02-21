from django.urls import re_path
from home.CardsPermutationsConsumer import CardsPermutationsConsumer
from home.GameOnePairConsumer import GameOnePairConsumer
from home.GatheringGamesConsumer import GatheringGamesConsumer
from home.DeepNeuralNetworkConsumer import DeepNeuralNetworkConsumer

websocket_urlpatterns = [
    re_path(r'ws/perms_combs/', CardsPermutationsConsumer.as_asgi()),
    re_path(r'ws/op_game/', GameOnePairConsumer.as_asgi()),
    re_path(r'ws/gathering_games/', GatheringGamesConsumer.as_asgi()),
    re_path(r'ws/deep_neural_network/', DeepNeuralNetworkConsumer.as_asgi()),
]