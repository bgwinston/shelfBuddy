from django.db import models
from django.conf import settings
from shelfbuddy_backend.users.models import CustomUser

RATING_CHOICES = [
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
]

class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_image = models.URLField(max_length=1000, blank=True)
    description = models.TextField(blank=True)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    source = models.CharField(max_length=20, default='manual')
    google_book_id = models.CharField(max_length=50, blank=True, null=True)
    total_pages = models.PositiveIntegerField(null=True, blank=True)
    
    date_added = models.DateTimeField(auto_now_add=True)
    genre = models.CharField(max_length=300, blank=True)

    READING_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=READING_STATUS_CHOICES, default='not_started')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)

    loaned_to = models.CharField(max_length=100, blank=True, null=True)
    loaned_to_phone = models.CharField(max_length=20, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    is_public = models.BooleanField(default=False)
    is_loaned = models.BooleanField(default=False)
    is_wishlist = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.author}"
    



