from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login-user'),  # Login user
    path('register/', views.register_user, name='register-user'),  # Register user
    path('logout/', views.logout_user, name='logout-user'),  # Logout user
]