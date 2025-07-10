from django.urls import path
from . import views  # ✅ Import the views module

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('post/', views.create_query, name='create_query'),
    path('queries/', views.query_list, name='query_list'),
    path('inbox/', views.inbox, name='inbox'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('query/<int:query_id>/', views.query_detail, name='query_detail'),
    path('chat/<str:username>/', views.chat_view, name='chat_view'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('users/', views.all_users_view, name='all_users'),
    path('query/<int:query_id>/delete/', views.delete_query, name='delete_query'),
    path('profile/<str:username>/', views.user_profile_view, name='user_profile'), 
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('answer/<int:answer_id>/delete/', views.delete_answer, name='delete_answer'),  
    path('my-queries/', views.my_queries_view, name='my_queries'),
    path('search/', views.search_view, name='search'),
    path('explore/', views.explore_view, name='explore'),
    path('explore/new/', views.create_post, name='create_post'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('chat/<str:username>/', views.chat_view, name='chat'),
    path('start-chat/<str:username>/', views.start_chat_view, name='start_chat'),
    path('migrate-now/', views.migrate_now, name='migrate_now'),
    path('load-data/', views.load_fixture_view, name='load_fixture'),
]
