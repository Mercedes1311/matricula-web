from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = [
        ('alumno', 'Alumno'),
        ('consejero', 'Consejero'),
    ]
    rol = models.CharField(max_length=10, choices=ROLES)
    alumno = models.OneToOneField('Alumno', on_delete=models.CASCADE, null=True, blank=True)

class Consejero(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    dni = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}"
    
class Admin(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    dni = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}"

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
    id_alumno = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10, default=1)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    dni = models.CharField(max_length=8)
    correo = models.EmailField(max_length=100)
    celular = models.CharField(max_length=9)
    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)
    anio = models.IntegerField(default=1)

    def __str__(self):
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

class Curso(models.Model):
    id = models.AutoField(primary_key=True) 
    codigo = models.CharField(max_length=10)
    nombre_curso = models.CharField(max_length=100) 
    semestre = models.IntegerField(default=1)
    creditos = models.IntegerField() 
    turno = models.CharField(
        max_length=1,
        choices=[('M', 'M'), ('T', 'T'), ('N', 'N')]
    )
    seccion = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')]) 
    prerrequisito = models.CharField(
        max_length=10, 
        null=True, 
        blank=True, 
    )
    anio = models.IntegerField(default=1)
    cupos_disponibles = models.IntegerField(default=30)  # Agregar este campo para cupos disponibles


    def __str__(self):
        return f"{self.codigo} - {self.nombre_curso} ({self.turno}{self.seccion})"

class CursoPrerrequisito(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.alumno} - {self.curso} (Fecha: {self.fecha})"

class Boucher(models.Model):
    id_boucher = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    numero_boucher = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Boucher {self.numero_boucher} - {self.alumno}"

class Matricula(models.Model):
    id_matricula = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    cursos = models.ManyToManyField(Curso)
    boucher = models.ManyToManyField(Boucher)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    fecha_matricula = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, default='pendiente')
    mensaje_rechazo = models.TextField(blank=True, null=True)
    mensaje_aprobacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Matricula {self.id_matricula} - Alumno: {self.alumno} - Estado: {self.estado}"
