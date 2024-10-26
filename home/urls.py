from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('permutacje', views.permutacje, name='home.permutacje'),
    path('run_script/', views.run_script, name='home.run_script'),
    path('task_status/<task_id>/', views.task_status, name='home.task_status'),
]