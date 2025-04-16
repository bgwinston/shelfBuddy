from django.urls import path
from .views import save_book_view, my_library_view, book_search, book_view, edit_book, delete_book

urlpatterns = [
path('save-book/', save_book_view, name='save-book'),
path('books/booksearch/', book_search, name='booksearch'),
path('books/mylibrary/', my_library_view, name='mylibrary'),
path('book/<str:book_id>/', book_view, name='bookview'),
path('books/edit/<int:book_id>/', edit_book, name='edit_book'),
path('books/delete/<int:book_id>/', delete_book, name='delete_book'),
]
