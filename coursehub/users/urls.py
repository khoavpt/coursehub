from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>', views.get_profile, name='get-profile'), # View user profile
    path('<int:user_id>/edit-profile/', views.edit_profile, name='edit-profile'), # Edit user profile
    path('<int:user_id>/enrolled-courses/', views.get_enrolled_courses, name='get-enrolled-courses'), # Get enrolled courses
]   