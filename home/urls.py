from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('permutacje_kart/', views.permutacje_kart, name='home.permutacje_kart'),
    path('start_task_view/', views.start_task, name='start_task_view'),
    path('stop_task_view/', views.stop_task, name='stop_task_view'), 
    path('permutacje_view/', views.permutacje, name='permutacje_view'),
    path('kombinacje_view/', views.kombinacje, name='kombinacje_view'),
    path('high_card_view/', views.high_card, name='high_card_view'),
    path('one_pair_view/', views.one_pair, name='one_pair_view'),
    path('two_pairs_view/', views.two_pairs, name='two_pairs_view'),
    path('three_of_a_kind_view/', views.three_of_a_kind, name='three_of_a_kind_view'),
    path('straight_view/', views.straight, name='straight_view'),
    path('color_view/', views.color, name='color_view'),
    path('full_view/', views.full, name='full_view'),
    path('carriage_view/', views.carriage, name='carriage_view'),
    path('straight_flush_view/', views.straight_flush, name='straight_flush_view'),
    path('straight_royal_flush_view/', views.straight_royal_flush, name='straight_royal_flush_view'),
    path('download_saved_file/', views.download_saved_file, name='download_saved_file'),
]