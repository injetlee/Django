from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=60)
    email = models.CharField(max_length=60, unique=True)
    password = models.CharField(max_length=60)

    def __str__(self):
        return self.name
