from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse



def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if role == 'vendor':
                    return redirect('vendor_login')
                else:
                    return redirect('login')

            if role == 'vendor':
                if hasattr(request.user, 'vendorprofile'):
                    return view_func(request, *args, **kwargs)
            elif role == 'user':
                if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'user':
                    return view_func(request, *args, **kwargs)

            return redirect('index')  # unauthorized
        return _wrapped_view
    return decorator
