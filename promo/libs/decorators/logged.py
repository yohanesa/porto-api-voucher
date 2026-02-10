from functools import wraps
from django.http import JsonResponse
from libs.exceptions.auth import IsNotAuthenticated


def require_authenticated(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
           raise IsNotAuthenticated()

        return func(request, *args, **kwargs)

    return wrapper
