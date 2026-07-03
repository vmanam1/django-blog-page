from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostViewsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("author", password="test-password-123")
        self.other_user = User.objects.create_user("other", password="test-password-123")
        self.post = Post.objects.create(
            title="Original title",
            content="Original content",
            author=self.author,
        )

    def test_home_lists_posts(self):
        response = self.client.get(reverse("blog-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_create_requires_authentication(self):
        response = self.client.get(reverse("post-create"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('post-create')}")

    def test_authenticated_user_can_create_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post-create"),
            {"title": "New post", "content": "New content"},
        )

        created = Post.objects.get(title="New post")
        self.assertRedirects(response, created.get_absolute_url())
        self.assertEqual(created.author, self.author)

    def test_non_author_cannot_update_post(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("post-update", args=[self.post.pk]),
            {"title": "Changed", "content": "Changed"},
        )

        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Original title")

    def test_author_can_delete_post(self):
        self.client.force_login(self.author)

        response = self.client.post(reverse("post-delete", args=[self.post.pk]))

        self.assertRedirects(response, reverse("blog-home"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
