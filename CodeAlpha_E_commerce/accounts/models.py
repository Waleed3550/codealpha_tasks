from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    AUTH_PROVIDER_EMAIL = "email"
    AUTH_PROVIDER_GOOGLE = "google"
    AUTH_PROVIDER_CHOICES = [
        (AUTH_PROVIDER_EMAIL, "Email and Password"),
        (AUTH_PROVIDER_GOOGLE, "Google"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDER_CHOICES, default=AUTH_PROVIDER_EMAIL)
    google_account_id = models.CharField(max_length=255, blank=True)
    is_email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=24, blank=True)
    avatar_url = models.URLField(blank=True)
    address_line_1 = models.CharField(max_length=180, blank=True)
    address_line_2 = models.CharField(max_length=180, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=80, default="United States")
    marketing_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"
