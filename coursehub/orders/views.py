from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from .forms import OrderForm
from courses.models import Course
import stripe
from django.http import JsonResponse 
from django.conf import settings
from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def enter_order_info(request, course_id):
    """
    View for entering order information.

    This view handles both GET and POST requests:
    - GET: Displays the order form
    - POST: Processes the submitted order form

    Args:
        request (HttpRequest): The incoming HTTP request.
        course_id (int): The ID of the course to order.

    Returns:
        HttpResponse: Renders the order form template or redirects to order payment verification.
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            user = User.objects.get(id=request.user.id)
            course = Course.objects.get(id=course_id)
            order = Order(user=user, course=course, total_amount=course.price, status='pending', payment_method=request.POST.get('payment_method'))
            order.save()
            print('Order created:', order)
            return redirect('get-order-summary', order_id=order.id)
    else:
        form = OrderForm()
        course = Course.objects.get(id=course_id)


    context = {'form': form, 'course': course}
    return render(request, 'orders/enter_order_info.html', context)

def handle_stripe_error(request, order, error):
    """
    Handles Stripe payment errors.

    This function renders the payment verification template with the error message.

    Args:
        request (HttpRequest): The incoming HTTP request.
        order (Order): The order object.
        error (StripeError): The Stripe error object.

    Returns:
        HttpResponse: Renders the payment verification template with the error message.
    """
    return render(request, 'orders/verify_order_payment.html', {
        'order': order,
        'error_message': str(error),
    })

@login_required
def verify_order_payment(request, order_id):
    """
    View for verifying order payment.

    This view handles the payment verification process for a specific order.
    It will handle Stripe payment and either complete the order or show an error.

    Args:
        request (HttpRequest): The incoming HTTP request.
        order_id (int): The ID of the order to verify.

    Returns:
        HttpResponse: Renders the payment verification template or redirects to order summary.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Stripe uses cents
                currency='usd',
                payment_method=request.POST.get('payment_method_id'),
                confirmation_method='manual',
                confirm=True
            )

            if intent['status'] == 'requires_action' and intent['next_action']['type'] == 'use_stripe_sdk':
                return JsonResponse({
                    'requires_action': True,
                    'payment_intent_client_secret': intent['client_secret']
                })
            elif intent['status'] == 'succeeded':
                order.status = 'completed'
                order.save()
                return redirect('orders:get_order_summary', order_id=order.id)

        except stripe.error.CardError as e:
            return handle_stripe_error(request, order, e)

    context = {'order': order, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY}
    return render(request, 'orders/verify_order_payment.html', context)

@login_required
def get_order_summary(request, order_id):
    """
    View for displaying order summary.

    This view shows a summary of the order after successful payment.

    Args:
        request (HttpRequest): The incoming HTTP request.
        order_id (int): The ID of the order to display.

    Returns:
        HttpResponse: Renders the order summary template.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'orders/order_summary.html', context)