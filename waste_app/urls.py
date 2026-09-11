from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new-request/',views.create_request,name='new-request'),
    
]