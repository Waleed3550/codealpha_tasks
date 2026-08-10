from django.contrib import admin

from assistant.models import AIConversation, AIMessage, AISettings, AIVoiceLog, Wishlist, WishlistItem


@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    list_display = ("assistant_name", "enabled", "provider", "default_model", "voice_enabled", "updated_at")


class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ("sender", "content", "language", "is_voice", "status", "created_at")


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "language", "last_message_at", "created_at")
    list_filter = ("language", "created_at")
    search_fields = ("session_key", "title", "user__username", "user__email")
    inlines = [AIMessageInline]


@admin.register(AIVoiceLog)
class AIVoiceLogAdmin(admin.ModelAdmin):
    list_display = ("language", "provider", "success", "user", "created_at")
    list_filter = ("language", "provider", "success", "created_at")
    search_fields = ("transcript", "response", "user__username")


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "updated_at")
    inlines = [WishlistItemInline]
