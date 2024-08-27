from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Course, Review
from users.models import UserProfile
import stripe
from unittest.mock import patch

class CourseModelTests(TestCase):
    """
    Test cases for the Course model.
    """

    def setUp(self):
        """
        Set up test data for Course model tests.
        """
        self.course_data = {
            'name': 'Test Course',
            'description': 'This is a test course',
            'institution': 'Test University',
            'course_url': 'https://testcourse.com',
            'price': Decimal('99.99'),
            'lecturer': 'Dr. Test',
            'level': 'Intermediate',
            'study_time': '30 hours'
        }

    @patch('stripe.Product.create')
    @patch('stripe.Price.create')
    def test_course_creation(self, mock_price_create, mock_product_create):
        """
        Test Course model creation and Stripe integration.
        """
        mock_product_create.return_value.id = 'prod_test123'
        mock_price_create.return_value.id = 'price_test123'

        course = Course.objects.create(**self.course_data)

        self.assertEqual(course.name, self.course_data['name'])
        self.assertEqual(course.price, self.course_data['price'])
        self.assertEqual(course.stripe_product_id, 'prod_test123')
        self.assertEqual(course.stripe_price_id, 'price_test123')

    @patch('stripe.Product.modify')
    @patch('stripe.Price.modify')
    @patch('stripe.Price.create')
    def test_course_update(self, mock_price_create, mock_price_modify, mock_product_modify):
        """
        Test Course model update and Stripe integration.
        """
        course = Course.objects.create(**self.course_data)
        
        course.name = 'Updated Test Course'
        course.price = Decimal('149.99')
        course.save()

        self.assertEqual(course.name, 'Updated Test Course')
        self.assertEqual(course.price, Decimal('149.99'))
        mock_product_modify.assert_called_once()
        mock_price_modify.assert_called_once()
        mock_price_create.assert_called_once()

class ReviewModelTests(TestCase):
    """
    Test cases for the Review model.
    """

    def setUp(self):
        """
        Set up test data for Review model tests.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            institution='Test Institution',
            course_url='https://testcourse.com',
            price=Decimal('99.99')
        )

    def test_review_creation(self):
        """
        Test Review model creation.
        """
        review = Review.objects.create(
            course=self.course,
            user=self.user,
            rating=4,
            review_text='Great course!'
        )

        self.assertEqual(review.course, self.course)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.review_text, 'Great course!')

class CourseViewsTests(TestCase):
    """
    Test cases for course-related views.
    """

    def setUp(self):
        """
        Set up test data and client for view tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Description',
            institution='Test Institution',
            course_url='https://testcourse.com',
            price=Decimal('99.99')
        )
        self.user_profile = UserProfile.objects.create(user=self.user)

    def test_home_page_view(self):
        """
        Test the home page view.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/home_page.html')

    def test_course_search_view(self):
        """
        Test the course search view.
        """
        response = self.client.get(reverse('course_search'), {'query': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_search.html')
        self.assertContains(response, 'Test Course')

    def test_course_detail_view(self):
        """
        Test the course detail view.
        """
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_detail.html')
        self.assertContains(response, 'Test Course')

    def test_enroll_course_view(self):
        """
        Test the enroll course view.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('enroll_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.course in self.user_profile.enrolled_courses.all())

    def test_review_course_view(self):
        """
        Test the review course view.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('review_course', args=[self.course.id]), {
            'rating': 5,
            'review_text': 'Excellent course!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Review.objects.filter(course=self.course, user=self.user).exists())

# Add more test classes and methods as needed
