from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    """
    Represents a course in the system.

    This model stores information about courses offered on the platform.
    It includes details such as the course title, description, instructor,
    price, and duration.

    Attributes:
        name (CharField): The title of the course.
        description (TextField): A brief description of the course.
        institution (CharField): The institution offering the course.
        course_url (URLField): The URL to the course page.
        price (DecimalField): The price of the course.
    """

    name = models.CharField(max_length=200)
    description = models.TextField()
    institution = models.CharField(max_length=50)
    course_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

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