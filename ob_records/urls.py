from django.urls import path
from . import views

urlpatterns = [
    # Officer pages
    path('', views.search, name='search'),  # 👈 Root URL goes to search
    path('record/<int:ob_id>/', views.record_detail, name='record_detail'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin pages
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/export/', views.export_csv, name='export_csv'),
    path('admin/create/', views.create_record, name='create_record'),
    path('admin/edit/<int:ob_id>/', views.edit_record, name='edit_record'),
    path('admin/delete/<int:ob_id>/', views.delete_record, name='delete_record'),

    # User Management
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/users/create/', views.create_user, name='create_user'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]