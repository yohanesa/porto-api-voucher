from functools import wraps
from django.http import JsonResponse
from libs.exceptions.auth import IsNotAuthorized


def require_authorized(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, "user", None)

        if not user.is_staff or not user.is_superuser:
           raise IsNotAuthorized()

        return func(request, *args, **kwargs)

    return wrapper


def require_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, "user", None)

        if not user.is_staff and user.admin == True or not user.is_superuser:
           raise IsNotAuthorized()

        return func(request, *args, **kwargs)

    return wrapper
