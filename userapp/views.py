from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def login_view(request):
    error = None
    username = request.POST.get('username') if request.method == 'POST' else ''

    if request.method == "POST":
        password = request.POST.get('password')

        # Check if user exists
        if not User.objects.filter(username=username).exists():
            error = "No account found with that username."
        else:
            # User exists → now check password
            user = authenticate(request, username=username, password=password)
            if user is None:
                error = "Incorrect password."
            else:
                login(request, user)
                return redirect('/dashboard/')

    return render(request, 'login.html', {'error': error, 'username': username})

def logout_view(request):
    logout(request)
    return redirect("/")



