from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect

def alumno_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'rol') and request.user.rol == 'alumno':
            return view_func(request, *args, **kwargs)
        return redirect('home')  
    return wrapper

def administrador_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'rol') and request.user.rol == 'administrador':
            return view_func(request, *args, **kwargs)
        return redirect('home')  
    return wrapper
