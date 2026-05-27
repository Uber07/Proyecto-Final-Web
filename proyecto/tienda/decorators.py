from django.shortcuts import redirect
from django.contrib import messages

def admin_requerido(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('tienda:login')
        if not request.user.is_staff:
            return redirect('tienda:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view