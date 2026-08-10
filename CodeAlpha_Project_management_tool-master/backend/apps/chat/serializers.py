from rest_framework import serializers
from .models import ChatRoom, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.email', read_only=True)
    sender_id = serializers.CharField(source='sender.id', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_id', 'content', 'is_edited', 'created_at', 'updated_at']

from .models import MessageReaction, ReadReceipt

class MessageReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReaction
        fields = '__all__'

class ReadReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadReceipt
        fields = '__all__'
