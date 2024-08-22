from django import forms
from .models import Order

PAYMENT_CHOICES = [
    ('credit_card', 'Credit Card'),
    ('paypal', 'PayPal'),
    ('bank_transfer', 'Bank Transfer')
]

class OrderForm(forms.ModelForm):
    """
    Form for creating a new order.

    This form allows users to select a payment method when placing an order.
    It includes validation to ensure that the payment method is not left blank.
    """

    class Meta:
        model = Order
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(choices=PAYMENT_CHOICES)
        }

    def clean_payment_method(self):
        """
        Validates the payment method field.

        Raises a ValidationError if the payment method is not provided.
        """
        payment_method = self.cleaned_data['payment_method']
        if not payment_method:
            raise forms.ValidationError("Payment method is required.")
        return payment_method