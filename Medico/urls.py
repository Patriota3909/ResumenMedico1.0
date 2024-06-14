# resúmenes/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('solicitud', views.solicitud, name='solicitud'),
   
]
