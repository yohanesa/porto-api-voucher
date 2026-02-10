from datetime import timedelta
from ninja import Router
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.utils import timezone
from libs.exceptions.auth import AuthError

from .models import ApiToken
from .schemas import (
    LoginSchema,
)

router = Router()

@router.post("/login")
def login(request, payload: LoginSchema):
    user = authenticate(
        username=payload.username,
        password=payload.password
    )

    if not user:
        raise AuthError()

    token = ApiToken.objects.create(
        user=user,
        token=ApiToken.generate(),
        expired_at=timezone.now() + timedelta(hours=12),
    )

    return {"token": token.token}