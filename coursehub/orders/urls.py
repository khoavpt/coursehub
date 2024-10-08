from django.urls import path
from . import views

urlpatterns = [
    path('<int:course_id>/enter-info', views.enter_order_info, name='enter-order-info'),  # Enter order information
    path('<int:order_id>/summary/', views.get_order_summary, name='get-order-summary'), # Get order summary  
    path('<int:order_id>/stripe-payment/', views.process_stripe_payment, name='process_stripe_payment'),
    # path('<int:order_id>/verify/', views.verify_order_payment, name='verify_order_payment'),  # Verify order payment
    path('<int:order_id>/verify-payment/', views.verify_order_payment, name='verify-order-payment'),
    path('<int:order_id>/success/', views.stripe_success, name='stripe-success'),

]