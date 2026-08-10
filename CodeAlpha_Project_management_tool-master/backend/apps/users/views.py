from rest_framework import viewsets, mixins, status, views, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import User, Profile
from .serializers import (
    UserSerializer, ProfileSerializer, RegisterSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .permissions import IsSelfOrAdmin

signer = TimestampSigner()

class AuthViewSet(viewsets.GenericViewSet):
    """
    Endpoints for Authentication (Registration, etc).
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], serializer_class=ChangePasswordSerializer)
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], serializer_class=ForgotPasswordSerializer)
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = signer.sign(str(user.id))
            # In a real scenario, we'd send an email here.
            # print(f"Reset token for {email}: {token}")
        except User.DoesNotExist:
            pass # Prevent user enumeration
        return Response({'detail': 'Password reset email sent if account exists.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], serializer_class=ResetPasswordSerializer)
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        try:
            # Token expires in 1 hour (3600 seconds)
            user_id = signer.unsign(token, max_age=3600)
            user = User.objects.get(id=user_id)
        except (BadSignature, SignatureExpired, User.DoesNotExist):
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            
            if 'refresh' in response.data:
                del response.data['refresh']
            
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                samesite='Lax',
                secure=not settings.DEBUG,
            )
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if refresh_token:
            request.data['refresh'] = refresh_token
            
        try:
            response = super().post(request, *args, **kwargs)
        except InvalidToken as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
        if response.status_code == 200:
            new_refresh_token = response.data.get('refresh')
            
            if 'refresh' in response.data:
                del response.data['refresh']
                
            if new_refresh_token:
                response.set_cookie(
                    'refresh_token',
                    new_refresh_token,
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                    httponly=True,
                    samesite='Lax',
                    secure=not settings.DEBUG,
                )
        return response

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            # If token is invalid or already blacklisted, still delete cookie to force logout
            response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            return response

class UserViewSet(viewsets.ModelViewSet):
    """
    Enterprise user retrieval and management endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy', 'activate', 'deactivate', 'change_role']:
            self.permission_classes = [IsAuthenticated, permissions.IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        serializer = self.get_serializer(request.user, data=request.data, partial=(request.method == 'PATCH'))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'User activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'User deactivated'})

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get('role')
        if role == 'superadmin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'admin':
            user.is_superuser = False
            user.is_staff = True
        elif role == 'employee':
            user.is_superuser = False
            user.is_staff = False
        else:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        user.save()
        return Response({'status': 'Role updated'})

class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Manage user preferences and avatars.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_avatar(self, request, pk=None):
        profile = self.get_object()
        if 'avatar' not in request.FILES:
            return Response({'error': 'No avatar file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.avatar = request.FILES['avatar']
        profile.save()
        return Response({'status': 'Avatar uploaded', 'avatar_url': profile.avatar.url})
