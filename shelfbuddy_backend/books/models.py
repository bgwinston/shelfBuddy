from django.db import models
from django.conf import settings

class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_image = models.URLField(max_length=1000, blank=True)
    description = models.TextField(blank=True)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=500)
    source = models.CharField(max_length=20, default='manual')
    
    date_added = models.DateTimeField(auto_now_add=True)
    genre = models.CharField(max_length=100, blank=True)

    READING_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=READING_STATUS_CHOICES, default='not_started')

    is_public = models.BooleanField(default=False)
    is_loaned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.author}"