from django.db import models

class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # You can hash later
    first_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    favorite_genre = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'users'  # 👈 This ensures the database table is called 'users'

    def __str__(self):
        return self.username