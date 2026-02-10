from ninja import Router
from django.shortcuts import get_object_or_404

from .models import Promo, VoucherCode
from .schemas import (
    PromoCreateSchema,
    PromoOutSchema,
    VoucherOutSchema,
    VoucherUpdateSchema,
)

from libs.decorators.logged import require_authenticated
from libs.decorators.authorization import require_authorized

router = Router()


@router.get("", response=list[PromoOutSchema])
@require_authenticated
@require_authorized
def list_promos(request):
    return Promo.objects.all()


@router.post("", response=PromoOutSchema)
@require_authenticated
@require_authorized
def create_promo(request, payload: PromoCreateSchema):
    promo = Promo.objects.create(
        name=payload.name,
        total_voucher=payload.total_voucher,
        type=payload.type,
        amount=payload.amount,
        min_discount=payload.min_discount,
        max_discount=payload.max_discount,
        min_purchase=payload.min_purchase,
    )
    return promo


@router.post("{promo_id}/vouchers", response=VoucherOutSchema)
@require_authenticated
@require_authorized
def create_voucher(request, promo_id: int):
    promo = get_object_or_404(Promo, id=promo_id)
    voucher = VoucherCode.objects.create(promo=promo)
    return voucher


@router.patch("/vouchers/{voucher_id}", response=VoucherOutSchema)
@require_authenticated
@require_authorized
def update_voucher(request, voucher_id: int, payload: VoucherUpdateSchema):
    voucher = get_object_or_404(VoucherCode, id=voucher_id)
    voucher.activated = payload.activated
    voucher.save()
    return voucher
