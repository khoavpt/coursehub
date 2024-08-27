from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import RegisterForm, LoginForm, UserForm, UserProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            location='Test Location',
            phone_number='123456789',
            birth_date=date(2000, 1, 1),
            gender='M'
        )

    def test_user_profile_creation(self):
        """Test that a UserProfile is correctly created and linked to the User."""
        self.assertEqual(self.user_profile.user.username, 'testuser')
        self.assertEqual(self.user_profile.location, 'Test Location')
        self.assertEqual(self.user_profile.gender, 'M')

    def test_str_method(self):
        """Test the __str__ method of UserProfile."""
        self.assertEqual(str(self.user_profile), 'testuser')


class UserViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = UserProfile.objects.create(user=self.user, gender='M')

    def test_get_profile_view(self):
        """Test the profile retrieval view."""
        url = reverse('get-profile', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_edit_profile_view(self):
        """Test the profile editing view."""
        self.client.login(username='testuser', password='password')
        url = reverse('edit-profile', args=[self.user.id])
        response = self.client.post(url, {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'location': 'Updated Location',
            'phone_number': '987654321',
            'birth_date': '1995-05-05',
            'gender': 'F'
        })
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user_profile.user.email, 'updated@example.com')
        self.assertEqual(self.user_profile.gender, 'F')

    def test_get_enrolled_courses_view(self):
        """Test the view that lists enrolled courses."""
        url = reverse('get-enrolled-courses', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/enrolled_courses.html')


class UserFormTest(TestCase):
    def test_valid_register_form(self):
        """Test that the registration form is valid with correct data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_register_form(self):
        """Test that the registration form is invalid with mismatched passwords."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'differentpassword'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_login_form(self):
        """Test that the login form is valid with correct credentials."""
        user = User.objects.create_user(username='testuser', password='password')
        form_data = {'username': 'testuser', 'password': 'password'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_login_form(self):
        """Test that the login form is invalid with incorrect credentials."""
        form_data = {'username': 'nonexistentuser', 'password': 'wrongpassword'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_valid_user_profile_form(self):
        """Test that the UserProfile form is valid with correct data."""
        form_data = {
            'location': 'Valid Location',
            'phone_number': '123456789',
            'birth_date': '2000-01-01',
            'gender': 'M'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_user_profile_form(self):
        """Test that the UserProfile form is invalid without a gender."""
        form_data = {
            'location': 'Valid Location',
            'phone_number': '123456789',
            'birth_date': '2000-01-01',
            'gender': ''
        }
        form = UserProfileForm(data=form_data)
        self.assertFalse(form.is_valid())

