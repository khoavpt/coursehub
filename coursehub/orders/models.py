from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now

class Order(models.Model):
    """
    Represents an order in the system.

    This model stores information about orders placed by users for courses.
    It includes details such as the user who placed the order, the course ordered,
    the order status, payment method, total amount, and a unique order number.

    Attributes:
        user (ForeignKey): The user who placed the order.
        course (ForeignKey): The course that was ordered.
        created_at (DateTimeField): The date and time when the order was created.
        updated_at (DateTimeField): The date and time when the order was last updated.
        status (CharField): The current status of the order (pending, completed, cancelled).
        payment_method (CharField): The method of payment used for the order.
        total_amount (DecimalField): The total amount of the order.
        order_number (CharField): The unique identifier for the order.
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

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username} for {self.course.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    """
    Automatically generates a unique order number for the order.

    This signal is triggered before the Order instance is saved.
    It generates a unique order number in the format "ORD-YYYYMMDDHHMMSS".
    """
    if not instance.order_number:
        instance.order_number = f"ORD-{now().strftime('%Y%m%d%H%M%S')}"