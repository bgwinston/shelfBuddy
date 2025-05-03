# reading/models.py
from django.db import models
from shelfbuddy_backend.users.models import CustomUser

class ReadingGoal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('books', 'Books'),
        ('pages', 'Pages'),
    ]
    TIME_PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey('ReadingPlan', on_delete=models.CASCADE, null=True, blank=True, related_name='goals')  # 🔗 NEW FIELD
    name = models.CharField(max_length=100)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    target_amount = models.PositiveIntegerField()
    time_period = models.CharField(max_length=20, choices=TIME_PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    completed_books = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s goal: {self.target_amount} {self.goal_type} ({self.time_period})"
    
class ReadingPlan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    start_date = models.DateField()
    target_end_date = models.DateField()
    daily_target_pages = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    @property
    def total_pages_read(self):
        return sum(progress.pages_read for progress in self.readingprogress_set.all())
    
class ReadingProgress(models.Model):
    plan = models.ForeignKey(ReadingPlan, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    pages_read = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.plan.book.title} on {self.date}: {self.pages_read} pages"
