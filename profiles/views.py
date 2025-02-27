from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    return render(request, 'profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', profile.bio)
        if 'profile_picture' in request.FILES:
            # Delete old image if it exists to avoid clutter
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect('profile', username=request.user.username)
    return render(request, 'profile.html', {'profile': profile})

@login_required
def follow(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.user.profile != profile:
        if profile in request.user.profile.following.all():
            request.user.profile.following.remove(profile)
        else:
            request.user.profile.following.add(profile)
    return redirect('profile', username=profile.user.username)