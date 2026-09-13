from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('new-request/',views.create_request,name='new-request'),
    path('my-request/',views.request_list,name='request_list'),
    path('register/', views.register_citizen, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='waste_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('update-status/<int:request_id>/<str:new_status>/', views.update_status, name='update_status'),

]