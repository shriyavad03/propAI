# property_recommender/views_auth.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'property_recommender/login.html')

@login_required
def home_view(request):
    username = request.user.username
    return render(request, 'property_recommender/newhome.html', {'username': username})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')