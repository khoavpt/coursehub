from django.urls import path
from . import views

urlpatterns = [
    path('recommends/<int:user_id>/', views.get_user_recommendations, name='get-user-recommendations'),  # Get user recommendations
]