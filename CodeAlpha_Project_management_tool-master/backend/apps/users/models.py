import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel

class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication instead of usernames."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Enterprise Custom User Model.
    Removes the username field and uses email for authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    
    # We don't inherit from BaseModel because AbstractUser already handles some fields,
    # but we add soft-delete capabilities for compliance.
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'auth_user'
        ordering = ['-date_joined']


class Profile(BaseModel):
    """
    User Profile for managing preferences, avatars, and extended user data.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.FileField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, max_length=1000)
    
    # User Preferences
    dark_mode_enabled = models.BooleanField(default=True)
    language_preference = models.CharField(max_length=10, default='en')
    timezone_preference = models.CharField(max_length=50, default='UTC')
    
    def __str__(self):
        return f"Profile: {self.user.email}"


class Invitation(BaseModel):
    """
    Handles inviting new users via email to the platform.
    """
    email = models.EmailField(db_index=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Invitation to {self.email}"
