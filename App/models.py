from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    alumno = models.OneToOneField('Alumno', on_delete=models.CASCADE, null=True, blank=True)

class Plan (models.Model):
    id_plan = models.AutoField(primary_key=True)
    nombre_plan = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_plan

class Escuela (models.Model):
    id_escuela = models.AutoField(primary_key=True)
    nombre_escuela = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_escuela

class Alumno(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10, default=1)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    dni = models.CharField(max_length=8)
    correo = models.EmailField(max_length=100)
    celular = models.CharField(max_length=9)
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno
