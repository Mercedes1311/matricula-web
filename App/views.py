from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm
from .models import Alumno, Usuario

@login_required
def home(request):
    return render(request, "home.html")

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data.get('codigo')

            try:
                alumno = Alumno.objects.get(codigo=codigo)
            except Alumno.DoesNotExist:
                messages.error(request, 'El código de alumno no existe.')
                return render(request, 'registro.html', {'form': form})

            usuario = form.save(commit=False)
            usuario.username = codigo
            usuario.alumno = alumno
            usuario.save()
            
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=codigo, password=raw_password)
            login(request, user)
            messages.success(request, 'Registro exitoso.')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
    else:
        form = LoginForm()
    return render(request, 'signin.html', {'form': form} )

def signout(request):
    logout(request)
    return redirect('signin')

def perfil(request, username):
    usuario = get_object_or_404(Usuario, username=username) 
    alumno = usuario.alumno
    return render(request, 'perfil.html', {'usuario': usuario, 'alumno': alumno})