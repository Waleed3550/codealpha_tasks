from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-response/', views.get_response, name='get_response'),
    path('chat-history/', views.chat_history, name='chat_history'),
    path('conversation/<int:conv_id>/', views.conversation_detail, name='conversation_detail'),
    
    # Internal frontend helpers
    path('get-messages/', views.get_messages_current, name='get_messages'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('search-chats/', views.search_chats, name='search_chats'),
]
