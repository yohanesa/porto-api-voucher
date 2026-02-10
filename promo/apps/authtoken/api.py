from datetime import timedelta
from ninja import Router
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.utils import timezone
from asgiref.sync import sync_to_async
from libs.exceptions.auth import AuthError

from .models import ApiToken
from .schemas import (
    LoginSchema,
)

router = Router()

@router.post("/login")
async def login(request, payload: LoginSchema):
    user = await sync_to_async(authenticate)(
        username=payload.username,
        password=payload.password,
    )

    if not user:
        raise AuthError()

    token_str = ApiToken.generate()

    token = await ApiToken.objects.acreate(
        user=user,
        token=token_str,
        expired_at=timezone.now() + timedelta(hours=12),
    )

    return {"token": token.token}