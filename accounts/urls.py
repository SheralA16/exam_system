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
]
