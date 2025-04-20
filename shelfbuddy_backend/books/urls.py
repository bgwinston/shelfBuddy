from django.urls import path
from .views import save_book_view, my_library_view, book_search, book_view, edit_book, delete_book,mybookshelf_view, loaned_books_view,book_detail_view, add_to_wishlist,wishlist_view,move_to_library

urlpatterns = [
path('save-book/', save_book_view, name='save-book'),
path('books/booksearch/', book_search, name='booksearch'),
path('books/mylibrary/', my_library_view, name='mylibrary'),
path('book/<str:book_id>/', book_view, name='bookview'),
path('books/edit/<int:book_id>/', edit_book, name='edit_book'),
path('books/delete/<int:book_id>/', delete_book, name='delete_book'),
path('books/view/<int:book_id>/', mybookshelf_view, name='mybookshelf_view'),
path('loans/', loaned_books_view, name='loaned_books'),
path('books/view/<int:book_id>/', book_detail_view, name='book_detail'),
path('wishlist/add/', add_to_wishlist, name='add_to_wishlist'),
path('wishlist/', wishlist_view, name='wishlist'),
path('books/<int:book_id>/move-to-library/', move_to_library, name='move_to_library'),
]
