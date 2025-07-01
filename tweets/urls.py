from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('like/<int:tweet_id>/', views.like_tweet, name='like_tweet'),
    path('comment/<int:tweet_id>/', views.add_comment, name='add_comment'),
    path('delete/<int:tweet_id>/', views.delete_tweet, name='delete_tweet'),
    path('notifications/', views.notifications, name='notifications'),
    path('search/', views.search, name='search'),
    path('search-users/', views.search_users, name='search_users'),  # New route

    # New professional features
    path('bookmark/<int:tweet_id>/', views.bookmark_tweet, name='bookmark_tweet'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('trending/', views.trending_hashtags, name='trending_hashtags'),
    path('hashtag/<str:hashtag>/', views.hashtag_tweets, name='hashtag_tweets'),
]