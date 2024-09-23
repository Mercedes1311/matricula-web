from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    usuario = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=10)

    def __str__(self):
        return self.usuario
