from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    usuario = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=10)

    def __str__(self):
        return self.usuario
    
class Alumno(models.Model):
    codigo_alumno = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    plan = models.CharField(max_length=50)
    dni = models.CharField(max_length=8)
    correo = models.EmailField()
    celular = models.CharField(max_length=15)
    escuela = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.codigo_alumno} - {self.nombres} {self.apellido_paterno}'
