import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, UserRegisterForm, UserUpdateForm

logger = logging.getLogger(__name__)


class SafePasswordResetView(PasswordResetView):
    """PasswordResetView that catches email-sending errors gracefully.

    When SMTP credentials are missing or invalid, Django's default view
    raises an unhandled exception and returns a 500 error.  This subclass
    catches those errors and re-renders the form with a user-friendly
    message instead.
    """

    template_name = "users/password_reset.html"

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception:
            logger.exception("Failed to send password-reset email")
            messages.error(
                self.request,
                "We were unable to send the password-reset email. "
                "Please try again later or contact the site administrator.",
            )
            return self.form_invalid(form)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created! You are now able to log in.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect("profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "users/profile.html", context)
