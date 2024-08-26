from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('<int:user_id>', views.get_profile, name='get-profile'), # View user profile
    path('<int:user_id>/edit-profile/', views.edit_profile, name='edit-profile'), # Edit user profile
    path('<int:user_id>/enrolled-courses/', views.get_enrolled_courses, name='get-enrolled-courses'), # Get enrolled courses
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)