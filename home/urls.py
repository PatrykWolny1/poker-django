from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('permutacje', views.permutacje, name='home.permutacje'),
    path('run_script/', views.run_script, name='run_script'),
]