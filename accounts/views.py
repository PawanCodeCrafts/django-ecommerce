from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .forms import UserSignUpForm, UserLoginForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.http import require_POST

def signup_view(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}')
            return redirect('shop:product_list')
    else:
        form = UserSignUpForm()

    return render(request, 'accounts/signup.html', {'form':form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST) 
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('shop:product_list')
        else:
            messages.error(request, 'Invalid Email or Password')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('shop:product_list')