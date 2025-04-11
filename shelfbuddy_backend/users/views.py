from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model



User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        favorite_genre = request.POST.get('favorite_genre', '')

        if favorite_genre == "Other":
            favorite_genre = request.POST.get('other_genre', '')

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {'error': 'Email already in use'})

        if password != request.POST.get('confirm_password'):
            return render(request, 'users/register.html', {'error': 'Passwords do not match'})

        # ✅ Use create_user so password is hashed properly
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            email=email,
            favorite_genre=favorite_genre
        )

        return redirect('login')

    return render(request, 'users/register.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})

    return render(request, 'users/login.html')


from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    return render(request, 'users/dashboard.html', {
        'first_name': request.user.first_name
    })


@login_required
def add_book_view(request):
    return render(request, 'books/booksearch.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')