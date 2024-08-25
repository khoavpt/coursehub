from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.timezone import now
import stripe
from django.conf import settings

# Configure Stripe API key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class Order(models.Model):
    """
    Represent an order in the system.

    This model stores information about orders placed by users for courses,
    including user details, course information, order status, and payment info.

    Attributes:
        user (ForeignKey): The user who placed the order.
        course (ForeignKey): The course that was ordered.
        created_at (DateTimeField): The date and time when the order was created.
        updated_at (DateTimeField): The date and time when the order was last updated.
        status (CharField): The current status of the order.
        payment_method (CharField): The method of payment used for the order.
        total_amount (DecimalField): The total amount of the order.
        order_number (CharField): A unique identifier for the order.
        stripe_checkout_session_id (CharField): The ID of the Stripe Checkout session.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """Return a string representation of the order."""
        return f"Order {self.order_number} by {self.user.username} for {self.course.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    """
    Generate a unique order number for new orders.

    This function is triggered before saving an Order instance.
    It creates a unique order number in the format "ORD-YYYYMMDDHHMMSS".

    Args:
        sender: The model class.
        instance: The actual instance being saved.
        **kwargs: Additional keyword arguments.
    """
    if not instance.order_number:
        instance.order_number = f"ORD-{now().strftime('%Y%m%d%H%M%S')}"

@receiver(post_save, sender=Order)
def create_stripe_checkout_session(sender, instance, created, **kwargs):
    """
    Create a Stripe Checkout Session for new orders with Stripe payment method.

    This function is triggered after saving an Order instance. It creates a new
    Checkout Session in Stripe with the order details.

    Args:
        sender: The model class.
        instance: The actual instance being saved.
        created (bool): True if a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created and instance.payment_method == 'stripe':
        # Create a Checkout Session in Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': instance.course.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=settings.HOST_URL + f'/orders/{instance.id}/success/',
            cancel_url=settings.HOST_URL + f'/orders/{instance.id}/cancel/',
            customer_email=instance.user.email,
        )
        # Update the order with the Stripe Checkout Session ID
        instance.stripe_checkout_session_id = checkout_session.id
        instance.save()