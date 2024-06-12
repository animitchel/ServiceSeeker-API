"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test Name',
            'last_name': 'Test last name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test Name',
            'last_name': 'Test last name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'first_name': 'Test Name',
            'last_name': 'Test last name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateUserApiTests(TestCase):
        """Test API requests that require authentication."""

        def setUp(self):
            self.user = create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test Name',
            )
            self.client = APIClient()
            self.client.force_authenticate(user=self.user)

        def test_retrieve_profile_success(self):
            """Test retrieving profile for logged in user."""
            res = self.client.get(ME_URL)

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data, {
                'first_name': self.user.first_name,
                'email': self.user.email,
            })

        def test_post_me_not_allowed(self):
            """Test POST is not allowed for the me endpoint."""
            res = self.client.post(ME_URL, {})

            self.assertEqual(
                res.status_code,
                status.HTTP_405_METHOD_NOT_ALLOWED
            )

        def test_update_user_profile(self):
            """Test updating the user profile for the authenticated user."""
            payload = {
                'first_name': 'Updated name',
                'password': 'newpassword123'
            }

            res = self.client.patch(ME_URL, payload)

            self.user.refresh_from_db()
            self.assertEqual(self.user.name, payload['first_name'])
            self.assertTrue(self.user.check_password(payload['password']))
            self.assertEqual(res.status_code, status.HTTP_200_OK)


class TokenObtainPairViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = 'test@example.com'
        self.password = 'testpassword123'
        self.first_name = 'Test'
        self.user = get_user_model().objects.create_user(
            email=self.email, password=self.password,
            first_name=self.first_name
        )
        self.token_url = reverse('user:token_obtain_pair')

    def test_token_obtain_pair(self):
        response = self.client.post(
            self.token_url, {
                'email': self.email,
                'password': self.password
            },
            format='json'
        )

        # Check if the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the access and refresh tokens
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_obtain_pair_invalid_credentials(self):
        response = self.client.post(
            self.token_url, {
                'email': self.email,
                'password': 'wrongpassword'
            },
            format='json'
        )

        # Check if the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check if the response contains the appropriate error message
        self.assertIn('detail', response.data)

    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        response = self.client.post(
            self.token_url, {
                'email': 'wrongtest@example.com',
                'password': self.password
            },
            format='json'
        )

        # Check if the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        # Check if the response contains the appropriate error message
        self.assertIn('detail', response.data)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        response = self.client.post(
            self.token_url, {
                'email': self.email, 'password': ""
            },
            format='json'
        )
        # Check if the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
