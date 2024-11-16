"""
URL configuration for pokerweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from home import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', include('home.urls')),
    
    path('', views.index, name='home.index'),
    path('cards_permutations/', views.cards_permutations, name='home.cards_permutations'),
    path('one_pair_game/', views.one_pair_game, name='home.one_pair_game'),
    
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
    path('submit_number/', views.submit_number, name='submit_number'),
    
    path('get_redis_value/', views.get_redis_value, name='get_redis_value'),
    path('start_game/', views.start_game, name='start_game'),   
]

if settings.DEBUG:
    print(settings.DEBUG, settings.STATIC_URL, settings.STATIC_ROOT, settings.BASE_DIR)
    print(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

