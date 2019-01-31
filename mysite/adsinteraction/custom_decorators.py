from functools import wraps
from django.shortcuts import redirect

def refresh_token(func):
    """
    Check if there is a valid refresh token in session
    """

    @wraps(func)
    def wrap(request, *args, **kwargs):

        if request.session.get('refresh_token'):
            return func(request, *args, **kwargs)
        
        return redirect('generate_refresh_token')

    return wrap