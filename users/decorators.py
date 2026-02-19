from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:login')
            
            if hasattr(request.user, 'profile'):
                if request.user.profile.role == required_role:
                    return view_func(request, *args, **kwargs)
                elif required_role == 'admin' and request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
            
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('users:dashboard')
        return wrapper
    return decorator


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        is_admin = False
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            is_admin = True
        elif request.user.is_superuser:
            is_admin = True
        
        if is_admin:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Admin access required.')
        return redirect('users:dashboard')
    return wrapper


def driver_required(view_func):
    return role_required('driver')(view_func)


def user_required(view_func):
    return role_required('user')(view_func)
