from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Story, ConnectionRequest
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add basic user info alongside the tokens
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        
        request = self.context.get('request')
        avatar_url = None
        try:
            if self.user.profile and self.user.profile.avatar and request:
                avatar_url = request.build_absolute_uri(self.user.profile.avatar.url)
        except Exception:
            pass
        data['avatar'] = avatar_url
        return data

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id', 'user_id', 'username', 'bio', 'avatar', 'follower_count', 'following_count')

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.profile_set.count()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url') and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

class PostAuthorSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')
        
    def get_avatar(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'profile') and obj.profile.avatar and hasattr(obj.profile.avatar, 'url') and request:
            return request.build_absolute_uri(obj.profile.avatar.url)
        return None

class PostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False, allow_blank=True)
    author = PostAuthorSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'author', 'content', 'image', 'video', 'like_count', 'comment_count', 'is_liked_by_me', 'created_at')
        read_only_fields = ('id', 'author', 'like_count', 'comment_count', 'is_liked_by_me', 'created_at')

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_video(self, obj):
        request = self.context.get('request')
        if obj.video and hasattr(obj.video, 'url') and request:
            return request.build_absolute_uri(obj.video.url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'post', 'author', 'created_at')

class StorySerializer(serializers.ModelSerializer):
    author = PostAuthorSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'author', 'image', 'video', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_video(self, obj):
        request = self.context.get('request')
        if obj.video and hasattr(obj.video, 'url') and request:
            return request.build_absolute_uri(obj.video.url)
        return None

class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender = PostAuthorSerializer(read_only=True)
    receiver = PostAuthorSerializer(read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ('id', 'sender', 'receiver', 'status', 'created_at')
        read_only_fields = ('id', 'sender', 'receiver', 'status', 'created_at')
