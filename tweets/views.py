from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Tweet, Comment, Bookmark, Notification, UserBlock, HashTag
from profiles.models import Profile
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib import messages
import mimetypes
import logging
import re

logger = logging.getLogger(__name__)

@login_required
def home(request):
    if request.method == 'POST':
        try:
            content = request.POST.get('content', '').strip()
            if not content:
                messages.error(request, 'Tweet content cannot be empty.')
                return redirect('home')
            
            if len(content) > 280:  # Twitter-like character limit
                messages.error(request, 'Tweet content must be 280 characters or less.')
                return redirect('home')
            
            tweet = Tweet(user=request.user, content=content)
            
            if 'media' in request.FILES:
                media_file = request.FILES['media']
                mime_type, _ = mimetypes.guess_type(media_file.name)
                
                # Check file size (5MB limit)
                if media_file.size > 5 * 1024 * 1024:
                    messages.error(request, 'File size must be less than 5MB.')
                    return redirect('home')
                
                if mime_type and mime_type.startswith('image'):
                    tweet.image = media_file
                elif mime_type and mime_type.startswith('video'):
                    tweet.video = media_file
                else:
                    messages.error(request, 'Only image and video files are allowed.')
                    return redirect('home')
            
            tweet.save()
            messages.success(request, 'Tweet posted successfully!')
            
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            messages.error(request, 'An error occurred while posting your tweet. Please try again.')
    
    try:
        following = request.user.profile.following.all()
    except Profile.DoesNotExist:
        following = []
        messages.info(request, 'Complete your profile to see tweets from people you follow.')
    except Exception as e:
        logger.error(f"Error getting following list: {str(e)}")
        following = []
    
    try:
        tweets = Tweet.objects.filter(user__profile__in=following) | Tweet.objects.filter(user=request.user)
        tweets = tweets.select_related('user').prefetch_related('likes', 'comments', 'bookmark_set').order_by('-created_at')
        trending = Tweet.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:5]
        
        # Add bookmark status for each tweet
        for tweet in tweets:
            tweet.is_bookmarked = tweet.bookmark_set.filter(user=request.user).exists()
            
    except Exception as e:
        logger.error(f"Error loading tweets: {str(e)}")
        tweets = Tweet.objects.none()
        trending = Tweet.objects.none()
        messages.error(request, 'Error loading tweets. Please refresh the page.')
    
    return render(request, 'home.html', {'tweets': tweets, 'trending': trending})

@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet.objects.select_related('user').prefetch_related('likes', 'comments', 'bookmark_set'), id=tweet_id)
    tweet.is_bookmarked = tweet.bookmark_set.filter(user=request.user).exists()
    return render(request, 'tweet_detail.html', {'tweet': tweet})

@login_required
def like_tweet(request, tweet_id):
    if request.method == 'POST':
        try:
            tweet = get_object_or_404(Tweet, id=tweet_id)
            if request.user in tweet.likes.all():
                tweet.likes.remove(request.user)
                is_liked = False
            else:
                tweet.likes.add(request.user)
                is_liked = True
            return JsonResponse({'likes': tweet.likes.count(), 'is_liked': is_liked})
        except Exception as e:
            logger.error(f"Error liking tweet {tweet_id}: {str(e)}")
            return JsonResponse({'error': 'Unable to like tweet'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def add_comment(request, tweet_id):
    if request.method == 'POST':
        try:
            tweet = get_object_or_404(Tweet, id=tweet_id)
            content = request.POST.get('content', '').strip()
            
            if not content:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
                messages.error(request, 'Comment cannot be empty')
                return redirect('tweet_detail', tweet_id=tweet_id)
            
            if len(content) > 280:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Comment must be 280 characters or less'}, status=400)
                messages.error(request, 'Comment must be 280 characters or less')
                return redirect('tweet_detail', tweet_id=tweet_id)
            
            Comment.objects.create(tweet=tweet, user=request.user, content=content)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'comments': tweet.comments.count()})
            
            messages.success(request, 'Comment added successfully!')
            return redirect('tweet_detail', tweet_id=tweet_id)
            
        except Exception as e:
            logger.error(f"Error adding comment to tweet {tweet_id}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Unable to add comment'}, status=500)
            messages.error(request, 'Error adding comment. Please try again.')
            return redirect('tweet_detail', tweet_id=tweet_id)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def delete_tweet(request, tweet_id):
    try:
        tweet = get_object_or_404(Tweet, id=tweet_id)
        if request.user == tweet.user:
            tweet.delete()
            messages.success(request, 'Tweet deleted successfully.')
        else:
            messages.error(request, 'You can only delete your own tweets.')
    except Exception as e:
        logger.error(f"Error deleting tweet {tweet_id}: {str(e)}")
        messages.error(request, 'Error deleting tweet. Please try again.')
    
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

@login_required
def bookmark_tweet(request, tweet_id):
    if request.method == 'POST':
        try:
            tweet = get_object_or_404(Tweet, id=tweet_id)
            bookmark, created = Bookmark.objects.get_or_create(user=request.user, tweet=tweet)
            
            if not created:
                bookmark.delete()
                is_bookmarked = False
            else:
                is_bookmarked = True
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'is_bookmarked': is_bookmarked,
                    'bookmarks_count': tweet.bookmark_set.count()
                })
            
            messages.success(request, 'Tweet bookmarked!' if is_bookmarked else 'Bookmark removed!')
            return redirect('tweet_detail', tweet_id=tweet_id)
            
        except Exception as e:
            logger.error(f"Error bookmarking tweet {tweet_id}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Unable to bookmark tweet'}, status=500)
            messages.error(request, 'Error bookmarking tweet. Please try again.')
            return redirect('tweet_detail', tweet_id=tweet_id)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def bookmarks(request):
    try:
        user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('tweet__user').prefetch_related('tweet__likes', 'tweet__comments', 'tweet__bookmark_set')
        
        # Add bookmark status for each tweet
        for bookmark in user_bookmarks:
            bookmark.tweet.is_bookmarked = True  # All tweets in bookmarks are bookmarked by definition
            
        return render(request, 'bookmarks.html', {'bookmarks': user_bookmarks})
    except Exception as e:
        logger.error(f"Error loading bookmarks for {request.user.username}: {str(e)}")
        messages.error(request, 'Error loading bookmarks. Please try again.')
        return redirect('home')

def process_tweet_content(content):
    """Process tweet content to extract mentions and hashtags"""
    mentions = re.findall(r'@(\w+)', content)
    hashtags = re.findall(r'#(\w+)', content)
    return mentions, hashtags

def create_notification(recipient, sender, notification_type, tweet=None, message=""):
    """Create a notification for user actions"""
    try:
        if recipient != sender:  # Don't notify yourself
            Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                tweet=tweet,
                message=message
            )
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")

@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        try:
            notification_ids = request.POST.getlist('notification_ids')
            if notification_ids:
                Notification.objects.filter(
                    id__in=notification_ids, 
                    recipient=request.user
                ).update(is_read=True)
            else:
                # Mark all as read
                Notification.objects.filter(
                    recipient=request.user, 
                    is_read=False
                ).update(is_read=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, 'Notifications marked as read!')
            return redirect('notifications')
            
        except Exception as e:
            logger.error(f"Error marking notifications as read: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Unable to mark notifications as read'}, status=500)
            messages.error(request, 'Error updating notifications. Please try again.')
            return redirect('notifications')
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def trending_hashtags(request):
    try:
        from django.db.models import Count
        trending = HashTag.objects.annotate(
            tweet_count=Count('tweets')
        ).filter(tweet_count__gt=0).order_by('-tweet_count')[:10]
        
        return render(request, 'trending.html', {'trending_hashtags': trending})
    except Exception as e:
        logger.error(f"Error loading trending hashtags: {str(e)}")
        messages.error(request, 'Error loading trending topics. Please try again.')
        return redirect('home')

@login_required
def hashtag_tweets(request, hashtag):
    try:
        hashtag_obj = get_object_or_404(HashTag, name=hashtag)
        tweets = hashtag_obj.tweets.all().select_related('user').prefetch_related('likes', 'comments', 'bookmark_set')
        
        # Add bookmark status for each tweet
        for tweet in tweets:
            tweet.is_bookmarked = tweet.bookmark_set.filter(user=request.user).exists()
        
        context = {
            'hashtag': hashtag_obj,
            'tweets': tweets
        }
        return render(request, 'hashtag_tweets.html', context)
    except Exception as e:
        logger.error(f"Error loading hashtag tweets for #{hashtag}: {str(e)}")
        messages.error(request, 'Error loading hashtag tweets. Please try again.')
        return redirect('home')