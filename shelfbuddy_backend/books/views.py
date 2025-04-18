import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from users.models import CustomUser  
from datetime import datetime


GENRE_CHOICES = [
    'Fiction',
    'Non-Fiction',
    'Fantasy',
    'Science Fiction',
    'Mystery',
    'Biography',
    'Romance',
    'Historical',
    'Thriller',
    'Self-Help',
    'Philosophy',
    'Children’s',
    'Young Adult',
    'Comics',
    'Poetry',
    'Education',
]

def book_search(request):
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
                    'genre': ', '.join(info.get('categories', [])),
                })

        context['results'] = books
        context['search_query'] = request.GET.get('q')

    return render(request, 'booksearch.html', context)

def book_view(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    # Fetch book details from Google Books
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
    if response.status_code != 200:
        return redirect('booksearch')

    info = response.json().get('volumeInfo', {})

    book = {
        'title': info.get('title'),
        'authors': ', '.join(info.get('authors', [])),
        'description': info.get('description', ''),
        'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
        'google_book_id': book_id,
    }

    return render(request, 'bookview.html', {'book': book})

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
        genre = request.POST.get('genre', '')
        description = request.POST.get('description', '')
        cover_image = request.POST.get('thumbnail', '')
        source = request.POST.get('source', 'manual')

        Book.objects.create(
            user=user,
            title=title,
            author=authors,
            genre=genre,
            description=description,
            cover_image=cover_image,
            source=source
        )

    return redirect('mylibrary')

def my_library_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    books = Book.objects.filter(user=user)  # loads all fields
    return render(request, 'mylibrary.html', {'books': books})

def edit_book(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    book = get_object_or_404(Book, id=book_id, user=user)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.description = request.POST.get('description')

        # Genre (choose or enter new)
        genre_existing = request.POST.get('genre_existing')
        genre_new = request.POST.get('genre_new')
        book.genre = genre_new.strip() if genre_new else genre_existing

        # Library type
        library_type = request.POST.get('library_type')
        book.is_public_library = (library_type == 'public')
        book.library_name = request.POST.get('library_name', '').strip() if book.is_public_library else ''

        # Loaned info
        is_loaned = request.POST.get('is_loaned')
        book.is_loaned = (is_loaned == 'yes')
        book.loaned_to = request.POST.get('loaned_to', '').strip() if book.is_loaned else ''

        # Due date (used for both public library and loaned)
        due_date_str = request.POST.get('due_date')
        if due_date_str:
            try:
                book.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                book.due_date = None
        else:
            book.due_date = None

        book.save()
        return redirect('mylibrary')

    return render(request, 'edit_book.html', {
        'book': book,
        'genres': GENRE_CHOICES
    })

def delete_book(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    book = get_object_or_404(Book, id=book_id, user=user)

    if request.method == 'POST':
        book.delete()
        return redirect('mylibrary')

    return redirect('edit_book', book_id=book.id)

def mybookshelf_view(request, book_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')

    book = get_object_or_404(Book, id=book_id, user=user)

    return render(request, 'mybookshelf.html', {'book': book})