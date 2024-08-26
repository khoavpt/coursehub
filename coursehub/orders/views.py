from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order
from .forms import OrderForm
from courses.models import Course
from django.conf import settings
import stripe

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def enter_order_info(request, course_id):
    """
    Handle the order information entry process.

    This view displays and processes the form for creating a new order.

    Args:
        request (HttpRequest): The request object.
        course_id (int): The ID of the course being ordered.

    Returns:
        HttpResponse: The rendered order information form or a redirect to the payment process.
    """
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.course = course
            order.total_amount = course.price
            order.save()
            if order.payment_method == 'stripe':
                return redirect('process_stripe_payment', order_id=order.id)
            return redirect('get-order-summary', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'orders/enter_order_info.html', {'form': form, 'course': course})

@login_required
def process_stripe_payment(request, order_id):
    """
    Process Stripe payment for an order.

    This view renders the Stripe payment page for the given order.

    Args:
        request (HttpRequest): The request object.
        order_id (int): The ID of the order being paid for.

    Returns:
        HttpResponse: The rendered Stripe payment page.
    """
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/stripe_payment.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_TEST_PUBLIC_KEY
    })

@login_required
def get_order_summary(request, order_id):
    """
    Display the summary of an order.

    This view shows the details of a specific order.

    Args:
        request (HttpRequest): The request object.
        order_id (int): The ID of the order to display.

    Returns:
        HttpResponse: The rendered order summary page.
    """
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_summary.html', {'order': order})

@login_required
def verify_order_payment(request, order_id):
    """
    Verify the payment status of an order.

    This view checks the payment status with Stripe and updates the order accordingly.

    Args:
        request (HttpRequest): The request object.
        order_id (int): The ID of the order to verify.

    Returns:
        HttpResponseRedirect: A redirect to the order summary page.
    """
    order = Order.objects.get(id=order_id)
    if order.payment_method == 'stripe':
        session = stripe.checkout.Session.retrieve(order.stripe_checkout_session_id)
        if session.payment_status == 'paid':
            order.status = 'completed'
            order.save()
    # Handle other payment methods here
    return redirect('get-order-summary', order_id=order.id)