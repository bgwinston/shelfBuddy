import requests
from django.shortcuts import render, redirect
from .models import Book
from users.models import CustomUser  
from users.models import CustomUser  


def add_book_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # User not logged in

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    context = {}

    if request.method == 'GET' and 'q' in request.GET:
        query = request.GET.get('q')
        search_type = request.GET.get('search_type', 'all')
        if search_type == 'title':
            query = f'intitle:{query}'
        elif search_type == 'author':
            query = f'inauthor:{query}'

        response = requests.get('https://www.googleapis.com/books/v1/volumes', params={
            'q': query,
            'maxResults': 10
        })

        books = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                info = item['volumeInfo']
                books.append({
                    'title': info.get('title'),
                    'authors': ', '.join(info.get('authors', [])),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
                    'google_book_id': item.get('id'),
                })

        context['results'] = books
        context['search_query'] = request.GET.get('q')

    return render(request, 'addbook.html', context)


def save_book_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors', '')
        description = request.POST.get('description', '')
        cover_image = request.POST.get('thumbnail', '')
        source = request.POST.get('source', 'manual')

        Book.objects.create(
            user=user,
            title=title,
            author=authors,
            description=description,
            cover_image=cover_image,
            source=source
        )

    return redirect('my-library')