from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login_user'),  # Login user
    path('register/', views.register_user, name='register_user'),  # Register user
]