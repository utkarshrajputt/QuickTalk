from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Tweet, Comment
from profiles.models import Profile
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

# Rest of the views remain unchanged...
@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    return render(request, 'tweet_detail.html', {'tweet': tweet})

@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
    else:
        tweet.likes.add(request.user)
    return JsonResponse({'likes': tweet.likes.count()})

@login_required
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == 'POST':
        content = request.POST['content']
        Comment.objects.create(tweet=tweet, user=request.user, content=content)
    return JsonResponse({'comments': tweet.comments.count()})

@login_required
def notifications(request):
    likes = Tweet.objects.filter(likes=request.user)
    follows = Profile.objects.filter(following=request.user.profile)
    return render(request, 'notifications.html', {'likes': likes, 'follows': follows})

@login_required
def search(request):
    query = request.GET.get('q', '')
    tweets = Tweet.objects.filter(content__icontains=query)
    profiles = Profile.objects.filter(user__username__icontains=query)
    return render(request, 'home.html', {'tweets': tweets, 'profiles': profiles, 'search_query': query})