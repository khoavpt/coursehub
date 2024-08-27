from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Order
from courses.models import Course
from unittest.mock import patch
import stripe

class OrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(title='Test Course', price=100.00)
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_create_order_with_missing_payment_method(self):
        """
        Test creating a new order with missing payment method.
        """
        url = reverse('orders:enter_order_info')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)
        self.assertFormError(response, 'form', 'payment_method', 'Payment method is required.')

    def test_verify_order_payment_with_card_error(self):
        """
        Test verifying order payment with a Stripe card error.
        """
        order = Order.objects.create(
            user=self.user,
            course=self.course,
            payment_method='credit_card',
            total_amount=100.00
        )
        url = reverse('orders:verify_order_payment', args=[order.id])
        with patch('stripe.PaymentIntent.create', side_effect=stripe.error.CardError('Card declined', 'param', 'code')):
            response = self.client.post(url, {'payment_method_id': 'pm_123456789'})
            self.assertContains(response, 'Card declined')

    def test_update_order_status(self):
        """
        Test updating the status of an order.
        """
        order = Order.objects.create(
            user=self.user,
            course=self.course,
            payment_method='credit_card',
            total_amount=100.00,
            status='pending'
        )
        order.status = 'completed'
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.status, 'completed')

    def test_list_user_orders(self):
        """
        Test displaying the list of orders for a user.
        """
        Order.objects.create(
            user=self.user,
            course=self.course,
            payment_method='credit_card',
            total_amount=100.00
        )
        url = reverse('orders:list_orders')
        response = self.client.get(url)
        self.assertContains(response, str(self.user.username))

    def test_order_number_uniqueness(self):
        """
        Test that order numbers are unique.
        """
        order1 = Order.objects.create(
            user=self.user,
            course=self.course,
            payment_method='credit_card',
            total_amount=100.00
        )
        order2 = Order.objects.create(
            user=self.user,
            course=self.course,
            payment_method='credit_card',
            total_amount=100.00
        )
        self.assertNotEqual(order1.order_number, order2.order_number)
