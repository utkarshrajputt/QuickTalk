from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Profile
import logging

logger = logging.getLogger(__name__)

@login_required
def profile_view(request, username):
    try:
        user = get_object_or_404(User, username=username)
        profile, created = Profile.objects.get_or_create(user=user)
        
        if created:
            messages.info(request, f'Profile created for {username}')
            logger.info(f"Created new profile for user: {username}")
        
        logger.info(f"Loading profile for user: {username}")
        
        # Get user's tweets
        from tweets.models import Tweet
        tweets = Tweet.objects.filter(user=user).select_related('user').prefetch_related('likes', 'comments', 'bookmark_set').order_by('-created_at')
        
        logger.info(f"Found {tweets.count()} tweets for user: {username}")
        
        # Add bookmark status for each tweet
        for tweet in tweets:
            tweet.is_bookmarked = tweet.bookmark_set.filter(user=request.user).exists()
        
        # Check if current user follows this profile
        is_following = False
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            try:
                is_following = profile in request.user.profile.following.all()
            except Exception as follow_error:
                logger.warning(f"Error checking follow status: {str(follow_error)}")
                is_following = False
        
        context = {
            'profile': profile,
            'tweets': tweets,
            'is_following': is_following,
            'is_own_profile': request.user == user,
        }
        
        logger.info(f"Rendering profile template for user: {username}")
        return render(request, 'profile.html', context)
        
    except User.DoesNotExist:
        logger.error(f"User not found: {username}")
        messages.error(request, f'User "{username}" not found.')
        return redirect('home')
    except Exception as e:
        logger.error(f"Error loading profile for {username}: {str(e)}")
        messages.error(request, 'Error loading profile. Please try again.')
        return redirect('home')

@login_required
def edit_profile(request):
    try:
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            bio = request.POST.get('bio', '').strip()
            
            if len(bio) > 500:  # Bio character limit
                messages.error(request, 'Bio must be 500 characters or less.')
                return redirect('edit_profile')
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                
                # Check file size (2MB limit)
                if profile_picture.size > 2 * 1024 * 1024:
                    messages.error(request, 'Profile picture must be less than 2MB.')
                    return redirect('edit_profile')
                
                # Check file type
                if not profile_picture.content_type.startswith('image/'):
                    messages.error(request, 'Only image files are allowed for profile pictures.')
                    return redirect('edit_profile')
                
                profile.profile_picture = profile_picture
            
            profile.bio = bio
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
            
    except Exception as e:
        logger.error(f"Error editing profile for {request.user.username}: {str(e)}")
        messages.error(request, 'Error updating profile. Please try again.')
    
    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def follow(request, profile_id):
    try:
        if request.method == 'POST':
            profile = get_object_or_404(Profile, id=profile_id)
            user_profile, created = Profile.objects.get_or_create(user=request.user)
            
            if user_profile == profile:
                messages.error(request, "You cannot follow yourself.")
                return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
            
            if profile in user_profile.following.all():
                user_profile.following.remove(profile)
                is_following = False
                messages.success(request, f"You unfollowed {profile.user.username}")
            else:
                user_profile.following.add(profile)
                is_following = True
                messages.success(request, f"You are now following {profile.user.username}")
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'is_following': is_following,
                    'followers_count': profile.followers.count()
                })
            
            return redirect('profile', username=profile.user.username)
            
    except Exception as e:
        logger.error(f"Error following/unfollowing profile {profile_id}: {str(e)}")
        messages.error(request, 'Error updating follow status. Please try again.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unable to update follow status'}, status=500)
    
    return redirect('home')