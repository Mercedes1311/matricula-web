from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Alumno

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