from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import UserRegisterForm, UserUpdateForm
from .models import Profile


class UserFormsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="test-password-123",
        )

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        form = UserRegisterForm(
            data={
                "username": "new-user",
                "email": "EXISTING@example.com",
                "password1": "new-test-password-123",
                "password2": "new-test-password-123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_user_can_keep_their_current_email(self):
        form = UserUpdateForm(
            data={"username": self.user.username, "email": self.user.email},
            instance=self.user,
        )

        self.assertTrue(form.is_valid())


class UserViewsTests(TestCase):
    def test_creating_user_creates_profile(self):
        user = User.objects.create_user("profile-owner", password="test-password-123")

        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_registration_creates_account_and_redirects_to_login(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-user",
                "email": "new@example.com",
                "password1": "new-test-password-123",
                "password2": "new-test-password-123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="new-user").exists())

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_logout_requires_post(self):
        user = User.objects.create_user("logout-user", password="test-password-123")
        self.client.force_login(user)

        get_response = self.client.get(reverse("logout"))
        post_response = self.client.post(reverse("logout"))

        self.assertEqual(get_response.status_code, 405)
        self.assertEqual(post_response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
