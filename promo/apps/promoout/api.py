from ninja import Router
from ninja.errors import ValidationError
from decimal import Decimal

from .schemas import RedeemSchema, RedeemResponseSchema
from .services.promo_service import PromoService

from libs.decorators.logged import require_authenticated

router = Router()


@router.post("redeem", response=RedeemResponseSchema)
@require_authenticated
def redeem(request, payload: RedeemSchema):
    """Redeem a voucher by its code.

    Delegates to PromoService which handles:
    - Pessimistic locking to prevent double-use
    - Strategy selection based on promo type
    - Calculation of discount/fees
    - Atomic activation of voucher

    Returns the redeemed voucher and calculation result.
    """
    try:
        transaction_amount = Decimal(str(payload.transaction_amount))
        result = PromoService.redeem_voucher(
            voucher_code=payload.code,
            transaction_pk=payload.transcation_pk,
            transaction_amount=transaction_amount,
        )
        return result
    except ValueError as e:
        raise ValidationError(str(e))
