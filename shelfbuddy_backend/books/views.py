import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from shelfbuddy_backend.users.models import CustomUser
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages



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

@login_required
def book_search(request):
    user = request.user
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

        saved_ids = set(Book.objects.filter(user=user, is_wishlist=False)
                        .values_list('google_book_id', flat=True))
        wishlist_ids = set(Book.objects.filter(user=user, is_wishlist=True)
                           .values_list('google_book_id', flat=True))

        context.update({
            'results': books,
            'search_query': request.GET.get('q'),
            'saved_ids': saved_ids,
            'wishlist_ids': wishlist_ids
        })

    return render(request, 'books/booksearch.html', context)

@login_required
def book_view(request, book_id):
    user = request.user
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
    info = response.json().get('volumeInfo', {})

    saved_book = Book.objects.filter(user=user, google_book_id=book_id).first()

    book = {
        'title': info.get('title'),
        'authors': ', '.join(info.get('authors', [])),
        'description': info.get('description', ''),
        'thumbnail': info.get('imageLinks', {}).get('thumbnail', ''),
        'rating': saved_book.rating if saved_book else None,
        'is_saved': bool(saved_book),
        'is_wishlist': saved_book.is_wishlist if saved_book else False,
        'google_book_id': book_id,
        'genre': ', '.join(info.get('categories', [])),
    }

    return render(request, 'books/bookview.html', {'book': book})

@login_required
def save_book_view(request):
    user = request.user

    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors', '')
        genre = request.POST.get('genre', '')
        description = request.POST.get('description', '')
        cover_image = request.POST.get('thumbnail', '')
        source = request.POST.get('source', 'manual')
        google_book_id = request.POST.get('google_book_id', '')

        # Optional: Prevent duplicates
        if google_book_id:
            existing = Book.objects.filter(user=user, google_book_id=google_book_id).first()
            if existing:
                return redirect('mylibrary')

        total_pages = None
        if google_book_id:
            try:
                response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{google_book_id}')
                if response.status_code == 200:
                    data = response.json()
                    total_pages = data.get('volumeInfo', {}).get('pageCount')
            except Exception as e:
                print(f"Error fetching page count: {e}")

        Book.objects.create(
            user=user,
            title=title,
            author=authors,
            genre=genre,
            description=description,
            cover_image=cover_image,
            source=source,
            google_book_id=google_book_id,
            total_pages=total_pages
        )

    return redirect('mylibrary')

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.description = request.POST.get('description')

        genre_existing = request.POST.get('genre_existing')
        genre_new = request.POST.get('genre_new')
        book.genre = genre_new.strip() if genre_new else genre_existing

        book.loaned_to = request.POST.get('loaned_to', '').strip()
        book.loaned_to_phone = request.POST.get('loaned_to_phone', '').strip()

        library_type = request.POST.get('library_type')
        book.is_public_library = (library_type == 'public')
        book.library_name = request.POST.get('library_name', '').strip() if book.is_public_library else ''

        is_loaned = request.POST.get('is_loaned')
        book.is_loaned = (is_loaned == 'yes')

        due_date_str = request.POST.get('due_date')
        if due_date_str:
            try:
                book.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                book.due_date = None
        else:
            book.due_date = None

        # Optional: save rating if included in form
        rating = request.POST.get('rating')
        if rating and rating.isdigit():
            book.rating = int(rating)

        book.save()
        return redirect('mylibrary')

    return render(request, 'books/edit_book.html', {
        'book': book,
        'genres': GENRE_CHOICES
    })


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        book.delete()
        return redirect('mylibrary')

    return redirect('edit_book', book_id=book.id)

@login_required
def mybookshelf_view(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    return render(request, 'books/mybookshelf.html', {'book': book})

@login_required
def loaned_books_view(request):
    loaned_books = Book.objects.filter(user=request.user, is_loaned=True)
    return render(request, 'books/loaned_books.html', {
        'loaned_books': loaned_books
    })


@login_required
def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    return render(request, 'books/book_detail.html', {'book': book})

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('authors', '')
        genre = request.POST.get('genre', '')
        description = request.POST.get('description', '')
        cover_image = request.POST.get('thumbnail', '')
        google_book_id = request.POST.get('google_book_id')
        source = request.POST.get('source', 'manual')

        if title:  # Ensure at least title exists
            Book.objects.create(
                user=request.user,
                title=title,
                author=author,
                genre=genre,
                description=description,
                cover_image=cover_image,
                source=source,
                google_book_id=google_book_id,
                is_wishlist=True
            )

    return redirect('wishlist')



@login_required
def wishlist_view(request):
    user = request.user
    wishlist_books = Book.objects.filter(user=user, is_wishlist=True)
    
    return render(request, 'books/wishlist_books.html', {
        'books': wishlist_books
    })

@login_required
def move_to_library(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user, is_wishlist=True)
    book.is_wishlist = False
    book.save()
    messages.success(request, f'"{book.title}" was successfully moved to your library.')
    return redirect('wishlist')

from django.db.models import Q

@login_required
def my_library_view(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(user=request.user),
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    else:
        books = Book.objects.filter(user=request.user)
    
    return render(request, 'books/mylibrary.html', {'books': books})

@login_required
def loan_instructions_view(request):
    return render(request, 'books/loan_instructions.html')