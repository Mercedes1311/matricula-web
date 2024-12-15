from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Alumno, Curso
from django.utils import timezone

class RegistroForm(UserCreationForm):
    codigo = forms.CharField(label='Código', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['codigo', 'password1', 'password2']

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if not Alumno.objects.filter(codigo=codigo).exists():
            raise forms.ValidationError("Este código de alumno no existe. Por favor verifique.")
        return codigo

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RecuperarContrasenaForm(forms.Form):
    codigo = forms.CharField(label='Código de Alumno', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dni = forms.CharField(label='DNI', max_length=8, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nueva_contrasena = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_contrasena = forms.CharField(label='Confirmar Contraseña',widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if nueva_contrasena != confirmar_contrasena:
            raise forms.ValidationError("Las contraseñas no coinciden.")

class FiltrarCursosForm(forms.Form):
    semestre = forms.ChoiceField(label="Semestre:", choices=[('1', 'Semestre 1'), ('2', 'Semestre 2')])

class MatriculaForm(forms.Form):
    numero_recibo1 = forms.CharField(label='Número del Primer Recibo: ', max_length=20, required=True)
    numero_recibo2 = forms.CharField(label='Número del Segundo Recibo: ', max_length=20, required=True)
