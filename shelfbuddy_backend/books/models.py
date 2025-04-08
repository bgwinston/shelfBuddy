from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.URLField(blank=True)
    source = models.CharField(max_length=20, default='manual')