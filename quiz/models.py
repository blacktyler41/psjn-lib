from django.db import models

class Book(models.Model):
    # The allowed categories. Each pair is (value saved in database, name shown to the user)
    CATEGORY_CHOICES = [
        ('religious', 'Religious'),
        ('science', 'Sciences'),
        ('other', 'Others'),
    ]

    title = models.CharField(max_length=200)
    Drive_link = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")

    def __str__(self):
        return self.title


