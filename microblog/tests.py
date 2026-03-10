from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from .models import Post, Like, Message

class MicroblogTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='u1@ex.com', password='password123', is_active=True)
        self.user2 = User.objects.create_user(username='user2', email='u2@ex.com', password='password123', is_active=True)
        self.client = Client()
        self.post = Post.objects.create(author=self.user1, content='Hello @user2')

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello')

    def test_post_create(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('post_create'), {'content': 'New Post'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_like_auth(self):
        self.client.login(username='user2', password='password123')
        response = self.client.post(reverse('post_like', kwargs={'pk': self.post.pk}))
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.first().user, self.user2)

    def test_post_like_anon(self):
        # Ensure session is created
        self.client.get(reverse('home'))
        response = self.client.post(reverse('post_like', kwargs={'pk': self.post.pk}))
        self.assertEqual(Like.objects.count(), 1)
        self.assertIsNone(Like.objects.first().user)
        self.assertIsNotNone(Like.objects.first().session_key)

    def test_message_send(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('message_send', kwargs={'username': 'user2'}), {'content': 'Secret message'})
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().recipient, self.user2)

    def test_mention_rendering(self):
        response = self.client.get(reverse('home'))
        # Should contain a link to user2's profile
        self.assertContains(response, f'href="{reverse("profile_view_user", kwargs={"username": "user2"})}"')

    def test_post_edit(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('post_edit', kwargs={'pk': self.post.pk}), {'content': 'Updated content'})
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'Updated content')

    def test_xss_prevention(self):
        xss_post = Post.objects.create(author=self.user1, content='<script>alert("xss")</script> @user2')
        response = self.client.get(reverse('home'))
        # The script tag should be escaped
        # Django's escape() also escapes quotes as &quot;
        self.assertContains(response, '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;')
        # But the mention should still be rendered as a link
        self.assertContains(response, f'href="{reverse("profile_view_user", kwargs={"username": "user2"})}"')
