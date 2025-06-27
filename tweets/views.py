from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Tweet, Comment
from profiles.models import Profile
from django.contrib.auth.models import User  # Add this import
from django.db.models import Count
import mimetypes

@login_required
def home(request):
    if request.method == 'POST':
        content = request.POST['content']
        tweet = Tweet(user=request.user, content=content)
        if 'media' in request.FILES:
            media_file = request.FILES['media']
            mime_type, _ = mimetypes.guess_type(media_file.name)
            if mime_type and mime_type.startswith('image'):
                tweet.image = media_file
            elif mime_type and mime_type.startswith('video'):
                tweet.video = media_file
        tweet.save()
    
    try:
        following = request.user.profile.following.all()
    except Profile.DoesNotExist:
        following = []
    
    tweets = Tweet.objects.filter(user__profile__in=following) | Tweet.objects.filter(user=request.user)
    trending = Tweet.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:5]
    return render(request, 'home.html', {'tweets': tweets, 'trending': trending})

@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    return render(request, 'tweet_detail.html', {'tweet': tweet})

@login_required
def like_tweet(request, tweet_id):
    if request.method == 'POST':
        tweet = get_object_or_404(Tweet, id=tweet_id)
        if request.user in tweet.likes.all():
            tweet.likes.remove(request.user)
            is_liked = False
        else:
            tweet.likes.add(request.user)
            is_liked = True
        return JsonResponse({'likes': tweet.likes.count(), 'is_liked': is_liked})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == 'POST':
        content = request.POST['content']
        Comment.objects.create(tweet=tweet, user=request.user, content=content)
    return JsonResponse({'comments': tweet.comments.count()})

@login_required
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.user == tweet.user:
        tweet.delete()
    return redirect('home')

@login_required
def notifications(request):
    liked_tweets = Tweet.objects.filter(user=request.user, likes__isnull=False).exclude(likes=request.user).distinct()
    new_followers = Profile.objects.filter(following=request.user.profile)
    return render(request, 'notifications.html', {'liked_tweets': liked_tweets, 'new_followers': new_followers})

@login_required
def search(request):
    query = request.GET.get('q', '')
    tweets = Tweet.objects.filter(content__icontains=query)
    profiles = Profile.objects.filter(user__username__icontains=query)
    return render(request, 'home.html', {'tweets': tweets, 'profiles': profiles, 'search_query': query})

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = None
    return render(request, 'search_users.html', {'users': users, 'query': query})