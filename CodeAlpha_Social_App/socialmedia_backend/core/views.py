from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Profile, Post, Comment, Story, ConnectionRequest
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer,
    ProfileSerializer, PostSerializer, CommentSerializer,
    StorySerializer, ConnectionRequestSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': {'user': serializer.data}
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            errors = serializer.errors if hasattr(serializer, 'errors') and serializer.errors else {'detail': str(e)}
            return Response({
                'success': False,
                'message': 'Authentication failed',
                'errors': errors
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        return Response({
            'success': True,
            'data': serializer.validated_data
        }, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            errors = serializer.errors if hasattr(serializer, 'errors') and serializer.errors else {'detail': str(e)}
            return Response({
                'success': False,
                'message': 'Token refresh failed',
                'errors': errors
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'success': True,
            'data': serializer.validated_data
        }, status=status.HTTP_200_OK)

def health_check(request):
    return JsonResponse({'success': True, 'message': 'API is running'})


# Profile Views
class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user__id'
    lookup_url_kwarg = 'user_id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

class UpdateProfileView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'user__id'
    lookup_url_kwarg = 'user_id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:
            return Response({'success': False, 'message': 'You can only update your own profile.'}, status=status.HTTP_403_FORBIDDEN)
        
        avatar = request.FILES.get('avatar') or request.data.get('avatar')
        
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        if avatar is not None:
            serializer.save(avatar=avatar)
        else:
            serializer.save()
        return Response({'success': True, 'data': serializer.data})

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response({'success': False, 'message': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        target_profile = get_object_or_404(Profile, user__id=user_id)
        target_profile.followers.add(request.user.profile)
        return Response({'success': True, 'message': 'Successfully followed user.'})

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target_profile = get_object_or_404(Profile, user__id=user_id)
        target_profile.followers.remove(request.user.profile)
        return Response({'success': True, 'message': 'Successfully unfollowed user.'})

# Post Views
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        content = request.data.get('content', '').strip()
        image = request.FILES.get('image') or request.data.get('image')
        video = request.FILES.get('video') or request.data.get('video')
        
        if not content and not image and not video:
            return Response({'success': False, 'message': 'At least one of content, image, or video is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, image=image, video=video)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)

class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = User.objects.filter(profile__followers=user.profile)
        return Post.objects.filter(models.Q(author__in=following_users) | models.Q(author=user))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

class PostDetailView(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({'success': False, 'message': 'You can only delete your own posts.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'success': True, 'message': 'Post deleted successfully.'})

class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return Response({'success': True, 'data': {'liked': liked}})

# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['pk'])

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post=post)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Story Views
class StoryListCreateView(generics.ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        image = request.FILES.get('image') or request.data.get('image')
        video = request.FILES.get('video') or request.data.get('video')
        
        if not image and not video:
            return Response({'success': False, 'message': 'Image or video is required for a story.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, image=image, video=video)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)

# Connection Views
class ConnectionRequestListView(generics.ListAPIView):
    serializer_class = ConnectionRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConnectionRequest.objects.filter(receiver=self.request.user, status='pending')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

class SendConnectionRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response({'success': False, 'message': 'Cannot send request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        receiver = get_object_or_404(User, pk=user_id)
        if ConnectionRequest.objects.filter(sender=request.user, receiver=receiver).exists() or \
           ConnectionRequest.objects.filter(sender=receiver, receiver=request.user).exists():
            return Response({'success': False, 'message': 'Request already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        ConnectionRequest.objects.create(sender=request.user, receiver=receiver)
        return Response({'success': True, 'message': 'Connection request sent.'})

class AcceptConnectionRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        req = get_object_or_404(ConnectionRequest, pk=pk, receiver=request.user, status='pending')
        req.status = 'accepted'
        req.save()
        # Add to connections
        request.user.profile.connections.add(req.sender.profile)
        return Response({'success': True, 'message': 'Connection request accepted.'})

class RejectConnectionRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        req = get_object_or_404(ConnectionRequest, pk=pk, receiver=request.user, status='pending')
        req.status = 'rejected'
        req.save()
        return Response({'success': True, 'message': 'Connection request rejected.'})

class ConnectionListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.connections.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'data': serializer.data})

class SuggestionListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        connected_profiles = user.profile.connections.all()
        # Exclude self and already connected
        # Also exclude pending sent/received requests to make it cleaner, but simple approach first
        exclude_users = [p.user.id for p in connected_profiles] + [user.id]
        
        # Exclude those we've sent requests to or received from
        sent_reqs = ConnectionRequest.objects.filter(sender=user).values_list('receiver_id', flat=True)
        recv_reqs = ConnectionRequest.objects.filter(receiver=user).values_list('sender_id', flat=True)
        exclude_users.extend(list(sent_reqs) + list(recv_reqs))
        
        return Profile.objects.exclude(user__id__in=exclude_users)[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'success': True, 'data': serializer.data})
