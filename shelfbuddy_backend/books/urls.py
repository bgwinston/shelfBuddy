from django.urls import path
from .views import add_book_view, save_book_view    

urlpatterns = [
path('add-book/', add_book_view, name='add-book'),
path('save-book/', save_book_view, name='save-book'),
path('add-book/', add_book_view, name='add-book'),
path('save-book/', save_book_view, name='save-book'),

]