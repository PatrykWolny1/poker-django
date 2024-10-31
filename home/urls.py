from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('permutacje', views.permutacje, name='home.permutacje'),
    path('progress/', views.start_task, name='home.progress'), 
    path('stop_task_view/', views.stop_task_view, name='stop_task_view'),  # Add this line 
    
    path('download_saved_file/', views.download_saved_file, name='download_saved_file'),
]