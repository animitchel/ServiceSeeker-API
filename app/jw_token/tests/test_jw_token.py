"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


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
        self.token_url = reverse('jw_token:token_obtain_pair')

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
