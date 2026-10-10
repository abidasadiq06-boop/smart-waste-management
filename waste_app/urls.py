from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    # =========================
    # BASIC PAGES
    # =========================

    path('', views.home, name='home'),

    path(
        'about/',
        views.about,
        name='about'
    ),

    path(
        'services/',
        views.services,
        name='services'
    ),

    path(
        'contact/',
        views.contact,
        name='contact'
    ),


    # =========================
    # LOGIN / LOGOUT
    # =========================

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
    'logout/',
    views.user_logout,
    name='logout'
),

    # =========================
    # CITIZEN
    # =========================

    path(
        'register/',
        views.register_citizen,
        name='register'
    ),

    path(
        'dashboard/',
        views.dashboard_redirect,
        name='dashboard'
    ),

    path(
        'citizen-dashboard/',
        views.citizen_dashboard,
        name='citizen_dashboard'
    ),

    path(
    'new-request/',
    views.create_request,
    name='new-request'  # The exact URL name
    ),

    path(
        'my-request/',
        views.request_list,
        name='request_list'
    ),


    # =========================
    # HKS WORKER
    # =========================

    path(
        'worker-dashboard/',
        views.worker_dashboard,
        name='worker_dashboard'
    ),

    path(
        'update-status/<int:request_id>/<str:new_status>/',
        views.update_status,
        name='update_status'
    ),


    path('download-receipt/<int:request_id>/', views.download_receipt, name='download_receipt'),


    # =========================
    # ADMIN DASHBOARD
    # =========================

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),


    

   

    # =========================
    # MANAGE HKS MEMBERS
    # =========================

    path(
        'manage-hks-members/',
        views.manage_hks_members,
        name='manage_hks_members'
    ),

    path(
        'add-hks-member/',
        views.add_hks_member,
        name='add_hks_member'
    ),

    path(
        'delete-hks-member/<int:member_id>/',
        views.delete_hks_member,
        name='delete_hks_member'
    ),


    # =========================
    # SCRAP MANAGEMENT
    # =========================

    path(
        'scrap-management/',
        views.scrap_management,
        name='scrap_management'
    ),

    path(
        'scrap-management/add/',
        views.add_scrap_item,
        name='add_scrap_item'
    ),

    path(
        'scrap-management/edit/<int:item_id>/',
        views.edit_scrap_item,
        name='edit_scrap_item'
    ),

    path(
        'scrap-management/delete/<int:item_id>/',
        views.delete_scrap_item,
        name='delete_scrap_item'
    ),


    # =========================
    # MONTHLY WASTE SCHEDULE
    # =========================

    path(
        'schedule/edit/<int:month>/',
        views.edit_schedule,
        name='edit_schedule'
    ),
    

]