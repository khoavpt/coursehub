from django.urls import path 
from . import views 

urlpatterns = [ 
    path('', views.home_page, name='home-page'),
    path('search/', views.course_search, name='course_search'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/review/', views.review_course, name='review_course'),
]