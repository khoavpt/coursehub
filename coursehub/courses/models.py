from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

class Course(models.Model):
    """
    Represents a course in the system.

    This model stores information about courses offered on the platform.
    It includes details such as the course title, description, institution,
    price, and Stripe integration details.

    Attributes:
        name (CharField): The title of the course.
        description (TextField): A brief description of the course.
        institution (CharField): The institution offering the course.
        course_url (URLField): The URL to the course page.
        price (DecimalField): The price of the course.
        stripe_product_id (CharField): The ID of the corresponding product in Stripe.
        stripe_price_id (CharField): The ID of the corresponding price in Stripe.
    """

    name = models.CharField(max_length=200)
    description = models.TextField()
    institution = models.CharField(max_length=50)
    course_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        """Return a string representation of the course."""
        return self.name

    def save(self, *args, **kwargs):
        # Làm sạch và kiểm tra giá
        try:
            cleaned_price = Decimal(str(self.price).split('.')[0] + '.' + str(self.price).split('.')[1][:2])
        except (IndexError, ValueError):
            raise ValueError(f"Invalid price value: {self.price}")

        if not self.stripe_product_id:
            # Create a new product in Stripe
            stripe_product_data = {
                "name": self.name,
            }
            if self.description:
                stripe_product_data["description"] = self.description
            
            stripe_product = stripe.Product.create(**stripe_product_data)
            self.stripe_product_id = stripe_product.id

            # Create a new price for the product in Stripe
            stripe_price = stripe.Price.create(
                product=self.stripe_product_id,
                unit_amount=int(cleaned_price * 100),  # Stripe uses cents
                currency='usd'
            )
            self.stripe_price_id = stripe_price.id
        else:
            # Update existing product in Stripe
            update_data = {"name": self.name}
            if self.description:
                update_data["description"] = self.description
            
            stripe.Product.modify(
                self.stripe_product_id,
                **update_data
            )

            # Update existing price in Stripe
            stripe.Price.modify(
                self.stripe_price_id,
                active=False
            )
            new_price = stripe.Price.create(
                product=self.stripe_product_id,
                unit_amount=int(cleaned_price * 100),
                currency='usd'
            )
            self.stripe_price_id = new_price.id

        # Cập nhật giá đã làm sạch
        self.price = cleaned_price

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override the delete method to handle Stripe product deletion.

        This method deactivates the corresponding product in Stripe when the course is deleted.
        """
        if self.stripe_product_id:
            stripe.Product.modify(self.stripe_product_id, active=False)
        super().delete(*args, **kwargs)

class Review(models.Model):
    """
    Represents a review for a course.

    This model stores information about reviews submitted by users for a course.
    It includes details such as the course, user, rating, and review text.

    Attributes:
        course (ForeignKey): The course being reviewed.
        user (ForeignKey): The user submitting the review.
        rating (IntegerField): The rating given by the user.
        review_text (TextField): The review text.
        review_date (DateTimeField): The date and time the review was submitted.
    """

    RATING_CHOICES = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.course.name} - {self.user.username}'