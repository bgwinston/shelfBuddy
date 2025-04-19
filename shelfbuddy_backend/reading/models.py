# reading/models.py
from django.db import models
from users.models import CustomUser
from books.models import Book

class ReadingPlan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField()
    target_end_date = models.DateField()
    daily_target_pages = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class ReadingProgress(models.Model):
    plan = models.ForeignKey(ReadingPlan, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    pages_read = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.plan.book.title} on {self.date}: {self.pages_read} pages"

class ReadingGoal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_books = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    completed_books = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.completed_books}/{self.target_books})"

