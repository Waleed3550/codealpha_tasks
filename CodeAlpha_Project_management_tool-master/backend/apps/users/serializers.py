from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from .models import User, Profile, Invitation

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'avatar', 'bio', 'dark_mode_enabled', 'language_preference', 'timezone_preference']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile', 'is_active', 'date_joined', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_active', 'date_joined', 'email', 'is_staff', 'is_superuser']

    def get_profile(self, obj):
        try:
            profile = obj.profile
        except ObjectDoesNotExist:
            profile, _ = Profile.objects.get_or_create(user=obj)
        return ProfileSerializer(profile, context=self.context).data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
        
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        Profile.objects.create(user=user)
        
        # Auto-create default Organization, Workspace, and Role
        from apps.organizations.models import Organization, Workspace, WorkspaceMember, Role
        org = Organization.objects.create(name=f"{user.first_name}'s Organization", owner=user)
        workspace = Workspace.objects.create(organization=org, name="My First Workspace")
        admin_role = Role.objects.create(workspace=workspace, name="Admin", permissions={"all": True})
        WorkspaceMember.objects.create(workspace=workspace, user=user, role=admin_role)

        return user

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ['id', 'token', 'is_accepted', 'created_at', 'updated_at']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
