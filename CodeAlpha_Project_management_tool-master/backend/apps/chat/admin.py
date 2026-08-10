from django.contrib import admin
from .models import ChatRoom, Message, MessageReaction, ReadReceipt

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    pass

@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    pass

