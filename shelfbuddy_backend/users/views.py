from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash



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

@login_required
def reading_dashboard(request):
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    return render(request, 'reading/reading_dashboard.html', {'plans': plans})

@login_required
def profile_view(request):
    return render(request, 'users/profile_view.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    user = request.user
    password_form = PasswordChangeForm(user=user, data=request.POST or None)

    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.email = request.POST.get('email', user.email)
        user.username = request.POST.get('username', user.username)

        # Genre handling
        genre = request.POST.get('favorite_genre')
        other = request.POST.get('other_genre', '').strip()
        user.favorite_genre = other if genre == 'Other' and other else genre

        try:
            user.save()
        except:
            return render(request, 'users/edit_profile.html', {
                'user': user,
                'password_form': password_form,
                'error': 'Failed to update profile info.'
            })

        # Handle password change
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, user)  # Keeps user logged in
            return redirect('profile')

        elif password_form.cleaned_data:
            return render(request, 'users/edit_profile.html', {
                'user': user,
                'password_form': password_form,
                'error': 'Password not updated. Please correct the errors below.'
            })

        return redirect('profile')

    return render(request, 'users/edit_profile_view.html', {
        'user': user,
        'password_form': password_form
    })