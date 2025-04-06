from .models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password  # DJango build in hashing function
from django.contrib.auth.hashers import check_password # Django build function

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        favorite_genre = request.POST.get('favorite_genre', '')

        if favorite_genre == "Other":
            favorite_genre = request.POST.get('other_genre', '')

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Username already exists'})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {'error': 'Email already in use'})

        # Optional: hash the password before saving
        hashed_password = make_password(password)

        CustomUser.objects.create(
            username=username,
            password=hashed_password,  # Use the hashed password
            first_name=first_name,
            email=email,
            favorite_genre=favorite_genre
        )

        return render(request, 'users/login.html', {'success': 'User registered! Login here!'})
        #return redirect('login')

    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = CustomUser.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                return redirect('dashboard') 
            else:
                return render(request, 'users/login.html', {'error': 'Incorrect password'})
        except CustomUser.DoesNotExist:
            return render(request, 'users/login.html', {'error': 'User not found'})

    return render(request, 'users/login.html')

from django.shortcuts import render, redirect
from .models import CustomUser

def dashboard_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')  # not logged in

    user = CustomUser.objects.get(id=user_id)

    return render(request, 'users/dashboard.html', {'username': user.username})

from django.shortcuts import redirect

def logout_view(request):
    request.session.flush()  # Clears all session data
    return redirect('login')  # Send them back to login page