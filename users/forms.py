from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024


class UniqueEmailMixin:
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        users = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            users = users.exclude(pk=self.instance.pk)
        if users.exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class UserRegisterForm(UniqueEmailMixin, UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserUpdateForm(UniqueEmailMixin, forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and image.size > MAX_PROFILE_IMAGE_SIZE:
            raise forms.ValidationError("Profile images must be 5 MB or smaller.")
        return image
