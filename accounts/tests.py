from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123', is_active=True)
        self.client = Client()

    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_profile_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '@testuser')

    def test_profile_edit(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_edit'), {
            'name': 'Test User',
            'location': 'Earth',
            'bio': 'I am a test user.',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Test User')
