from django import forms
from .models import Order

PAYMENT_CHOICES = [
    ('stripe', 'Credit Card (Stripe)'),
    ('bank_transfer', 'Bank Transfer'),
]

class OrderForm(forms.ModelForm):
    """
    Form for creating a new order.

    This form allows users to select a payment method when placing an order.
    It includes validation to ensure that the payment method is not left blank.

    Attributes:
        payment_method (Select): Dropdown for selecting the payment method.
    """

    PAYMENT_CHOICES = [
        ('stripe', 'Credit Card (Stripe)'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Order
        fields = ['payment_method']


    def clean_payment_method(self):
        """
        Validate the payment method field.

        This method checks if a payment method has been selected.

        Returns:
            str: The selected payment method.

        Raises:
            ValidationError: If no payment method is selected.
        """
        payment_method = self.cleaned_data['payment_method']
        if not payment_method:
            raise forms.ValidationError("Payment method is required.")
        return payment_method