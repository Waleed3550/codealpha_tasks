from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class AISettings(models.Model):
    PROVIDER_LOCAL = "local"
    PROVIDER_OPENAI = "openai"
    PROVIDER_GEMINI = "gemini"
    PROVIDER_CHOICES = [
        (PROVIDER_LOCAL, "Local Rules Engine"),
        (PROVIDER_OPENAI, "OpenAI Responses API"),
        (PROVIDER_GEMINI, "Google Gemini API"),
    ]

    assistant_name = models.CharField(max_length=80, default="CA-Tech AI")
    enabled = models.BooleanField(default=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_LOCAL)
    default_model = models.CharField(max_length=120, default="gpt-4.1-mini")
    openai_api_key_env = models.CharField(max_length=120, default="OPENAI_API_KEY")
    gemini_api_key_env = models.CharField(max_length=120, default="GEMINI_API_KEY")
    system_prompt = models.TextField(default="You are CA-Tech Electronics AI Shopping Assistant.")
    welcome_message = models.TextField(
        default="Hello. Welcome to CA-Tech Electronics. How can I help you today?"
    )
    supported_languages = models.JSONField(default=list, blank=True)
    voice_enabled = models.BooleanField(default=True)
    auto_detect_language = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Settings"
        verbose_name_plural = "AI Settings"

    def __str__(self):
        return self.assistant_name

    @classmethod
    def load(cls):
        settings_obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "supported_languages": ["en", "ur", "roman_ur", "roman_en", "mixed"],
            },
        )
        if not settings_obj.supported_languages:
            settings_obj.supported_languages = ["en", "ur", "roman_ur", "roman_en", "mixed"]
            settings_obj.save(update_fields=["supported_languages"])
        return settings_obj


class AIConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="ai_conversations")
    session_key = models.CharField(max_length=80, db_index=True)
    title = models.CharField(max_length=160, blank=True)
    language = models.CharField(max_length=24, default="en")
    memory = models.JSONField(default=dict, blank=True)
    source_page = models.CharField(max_length=300, blank=True)
    last_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-last_message_at",)
        indexes = [
            models.Index(fields=["session_key", "last_message_at"], name="ai_convo_session_idx"),
        ]

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class AIMessage(models.Model):
    SENDER_USER = "user"
    SENDER_ASSISTANT = "assistant"
    SENDER_SYSTEM = "system"
    SENDER_CHOICES = [
        (SENDER_USER, "User"),
        (SENDER_ASSISTANT, "Assistant"),
        (SENDER_SYSTEM, "System"),
    ]

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=16, choices=SENDER_CHOICES)
    content = models.TextField()
    language = models.CharField(max_length=24, default="en")
    is_voice = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=24, default="sent")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["conversation", "created_at"], name="ai_msg_convo_idx"),
        ]

    def __str__(self):
        return f"{self.sender}: {self.content[:40]}"


class AIVoiceLog(models.Model):
    conversation = models.ForeignKey(AIConversation, null=True, blank=True, on_delete=models.SET_NULL, related_name="voice_logs")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="ai_voice_logs")
    transcript = models.TextField()
    response = models.TextField(blank=True)
    language = models.CharField(max_length=24, default="en")
    provider = models.CharField(max_length=24, default="local")
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.language} voice log"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="wishlists")
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "session_key"], name="wishlist_user_session_idx")]

    def __str__(self):
        return f"Wishlist #{self.pk}"

    @property
    def item_count(self):
        return self.items.count()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist", "product")
        ordering = ("-added_at",)

    def __str__(self):
        return self.product.name
