from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Alumno

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", max_length=100)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['codigo_alumno', 'nombres', 'apellido_paterno', 'apellido_materno', 'plan', 'dni', 'correo', 'celular', 'escuela']
    
    codigo_alumno = forms.CharField(label="Código de Alumno", max_length=10)
    nombres = forms.CharField(label="Nombres", max_length=100)
    apellido_paterno = forms.CharField(label="Apellido Paterno", max_length=100)
    apellido_materno = forms.CharField(label="Apellido Materno", max_length=100)
    plan = forms.CharField(label="Plan", max_length=50)
    dni = forms.CharField(label="DNI", max_length=8)
    correo = forms.EmailField(label="Correo Electrónico")
    celular = forms.CharField(label="Celular", max_length=9)
    escuela = forms.CharField(label="Escuela", max_length=100)