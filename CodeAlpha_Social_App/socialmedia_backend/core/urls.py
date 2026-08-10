from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='auth_register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/refresh/', views.CustomTokenRefreshView.as_view(), name='auth_refresh'),
    
    # Profiles
    path('users/<int:user_id>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('users/<int:user_id>/update/', views.UpdateProfileView.as_view(), name='profile_update'),
    path('users/<int:user_id>/follow/', views.FollowUserView.as_view(), name='user_follow'),
    path('users/<int:user_id>/unfollow/', views.UnfollowUserView.as_view(), name='user_unfollow'),
    
    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post_list_create'),
    path('posts/feed/', views.FeedView.as_view(), name='post_feed'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/like/', views.LikePostView.as_view(), name='post_like'),
    
    # Comments
    path('posts/<int:pk>/comments/', views.CommentListCreateView.as_view(), name='post_comments'),
    
    # Stories
    path('stories/', views.StoryListCreateView.as_view(), name='story_list_create'),
    
    # Connections
    path('connections/requests/', views.ConnectionRequestListView.as_view(), name='connection_requests'),
    path('connections/requests/send/<int:user_id>/', views.SendConnectionRequestView.as_view(), name='send_connection_request'),
    path('connections/requests/<int:pk>/accept/', views.AcceptConnectionRequestView.as_view(), name='accept_connection_request'),
    path('connections/requests/<int:pk>/reject/', views.RejectConnectionRequestView.as_view(), name='reject_connection_request'),
    path('connections/', views.ConnectionListView.as_view(), name='connection_list'),
    path('connections/suggestions/', views.SuggestionListView.as_view(), name='connection_suggestions'),
]
