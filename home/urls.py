from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('permutacje_kart/', views.permutacje_kart, name='home.permutacje_kart'),
    path('start_task_view/', views.start_task, name='start_task_view'),
    path('stop_task_view/', views.stop_task, name='stop_task_view'), 
    path('permutacje_view/', views.permutacje, name='permutacje_view'),
    path('kombinacje_view/', views.kombinacje, name='kombinacje_view'),
    path('download_saved_file/', views.download_saved_file, name='download_saved_file'),
]