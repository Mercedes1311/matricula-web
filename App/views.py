from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, AlumnoForm
from .models import Usuario

# @login_required
def home(request):
    return render(request, "home.html")

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            
            if Usuario.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso. Por favor elige otro.')
            else:
                user = form.save()
                login(request, user)
                messages.success(request, '¡Registro exitoso! Puedes iniciar sesión ahora.')
                return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'signin.html', {'form': form})

def signout(request):
    logout(request)
    return redirect('signin')

def matricula_view(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()  # Esto guarda los datos en la base de datos  
            messages.success(request, 'Datos del alumno guardados con éxito.')          
            return redirect('matricula_view')  # Redirigir a una página de confirmación o donde quieras
    else:
        form = AlumnoForm()
    return render(request, 'matricula.html', {'form': form})
