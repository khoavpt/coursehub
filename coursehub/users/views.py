from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, logout, login

from .models import UserProfile
from .forms import RegisterForm, LoginForm, UserForm, UserProfileForm

# Create your views here.
def get_profile(request, user_id):
    if request.method == 'GET':
        user = get_object_or_404(User, id=user_id)
        user_profile = get_object_or_404(UserProfile, user=user)
        return render(request, 'users/profile.html', {'user': user, 'user_profile': user_profile})
    else:
        return HttpResponse('Method not allowed')

def edit_profile(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user_profile = get_object_or_404(UserProfile, user=user)
        user_form = UserForm(request.POST, instance=user)
        user_profile_form = UserProfileForm(request.POST, instance=user_profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            return redirect('get-profile', user_id=user_id)
    else:
        user = get_object_or_404(User, id=user_id)
        user_profile = get_object_or_404(UserProfile, user=user)
        user_form = UserForm(instance=user)
        user_profile_form = UserProfileForm(instance=user_profile)
    return render(request, 'users/edit_profile.html', {'user_form': user_form, 'user_profile_form': user_profile_form})

def get_enrolled_courses(request, user_id):
    if request.method == 'GET':
        user = get_object_or_404(User, id=user_id)
        user_profile = get_object_or_404(UserProfile, user=user)
        enrolled_courses = user_profile.enrolled_courses.all()
        return render(request, 'users/enrolled_courses.html', {'user': user, 'enrolled_courses': enrolled_courses})
    

def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(username, password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home-page')
            else:
                return HttpResponse('Invalid login')
        else:
            print(f"Form errors: {form.errors.as_json()}")
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
             # Create a UserProfile instance for the new user
            UserProfile.objects.create(user=user)
            login(request, user)

            return redirect('home-page')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('home-page')
