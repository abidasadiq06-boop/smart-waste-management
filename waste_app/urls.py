from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),  
    path('new-request/', views.create_request, name='new-request'),
    path('my-request/', views.request_list, name='request_list'),
    path('register/', views.register_citizen, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='waste_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('update-status/<int:request_id>/<str:new_status>/', views.update_status, name='update_status'),
    path('citizen-dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-citizens/',views.manage_citizens,name='manage_citizens'),
    path('manage-hks-members/', views.manage_hks_members, name='manage_hks_members'),
    path('add-hks-member/', views.add_hks_member, name='add_hks_member'),
]