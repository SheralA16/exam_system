from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/assign-courses/', views.student_assign_courses, name='student_assign_courses'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/reset-login-count/', views.reset_user_login_count, name='reset_user_login_count'),
    path('users/<int:user_id>/reset-axes/', views.reset_axes_for_user, name='reset_axes_for_user'),
    path('get-users-data/', views.get_users_data, name='get_users_data'),

    # Reactivación de cuentas
    path('request-reactivation/', views.request_reactivation, name='request_reactivation'),
    path('reactivation-requests/', views.reactivation_requests, name='reactivation_requests'),
    path('reactivation-requests/<int:request_id>/approve/', views.approve_reactivation, name='approve_reactivation'),
    path('reactivation-requests/<int:request_id>/reject/', views.reject_reactivation, name='reject_reactivation'),
    path('reactivation-requests/<int:request_id>/delete/', views.delete_reactivation_request, name='delete_reactivation_request'),
    path('get-pending-requests-count/', views.get_pending_requests_count, name='get_pending_requests_count'),
]
