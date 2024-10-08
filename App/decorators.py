from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect

def consejero_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'rol') and request.user.rol == 'consejero':
            return view_func(request, *args, **kwargs)
        return redirect('home')  
    return wrapper
