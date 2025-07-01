from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  # Add this import

def signup(request):
    if request.method == 'POST':
        try:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, f'Account created successfully for {user.username}! Please log in.')
                return redirect('login')
            else:
                # Display form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            form = UserCreationForm()
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            
            if not username or not password:
                messages.error(request, 'Please provide both username and password.')
                return render(request, 'login.html')
            
            user = authenticate(request, username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Your account has been deactivated.')
            else:
                messages.error(request, 'Invalid username or password.')
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again.')
    
    return render(request, 'login.html')

def logout_view(request):
    try:
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            messages.success(request, f'You have been logged out successfully, {username}!')
        else:
            messages.info(request, 'You are already logged out.')
    except Exception as e:
        messages.error(request, 'An error occurred during logout.')
    
    return redirect('login')