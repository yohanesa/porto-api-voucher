from django.urls import path, include
from django.http import JsonResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError
from ninja.security import django_auth
from .authtoken.api import router as auth_router
from .promoin.api import router as promo_router
from .promoout.api import router as promoout_router
from libs.exceptions.base import BaseError

api = NinjaAPI(
    title="Promo Code API",
    version="1.0",)

@api.exception_handler(BaseError)
def auth_error_handler(request, exc):
    return JsonResponse(
        {
            "code": exc.code,
            "description": exc.message,
        },
        status=401,
    )

api.add_router("auth/", auth_router)
api.add_router("promo/", promo_router)
api.add_router("promoout/", promoout_router)

urlpatterns = [
    path("api/", api.urls),
]
