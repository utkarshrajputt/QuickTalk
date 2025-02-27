from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('like/<int:tweet_id>/', views.like_tweet, name='like_tweet'),
    path('comment/<int:tweet_id>/', views.add_comment, name='add_comment'),
    path('notifications/', views.notifications, name='notifications'),
    path('search/', views.search, name='search'),
]