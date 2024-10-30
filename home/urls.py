from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('permutacje', views.permutacje, name='home.permutacje'),
    # path('input_form/', views.data, name='home.input_form'),
    path('start-task/', views.start_task, name='home.start_task'),  
    path('download_saved_file/', views.download_saved_file, name='download_saved_file'),
]