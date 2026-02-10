from decimal import Decimal
from typing import Dict, Any, Type

from django.db import transaction

from apps.promoin.models import VoucherCode
from apps.promoout.strategies.discount_fixed import DiscountFixedStrategy
from apps.promoout.strategies.discount_percentage import DiscountPercentageStrategy
from apps.promoout.strategies.free_shipping import FreeShippingStrategy
from apps.promoout.strategies.base import BaseStrategy


# Map promo.type to strategy class. Keep mapping simple and local to service.
STRATEGY_MAP: dict[str, Type[BaseStrategy]] = {
    "fixed": DiscountFixedStrategy,
    "percentage": DiscountPercentageStrategy,
    "free_shipping": FreeShippingStrategy,
}


class PromoService:
    @staticmethod
    def _get_strategy_for_voucher(vc: VoucherCode) -> BaseStrategy:
        strategy_cls = STRATEGY_MAP.get(vc.promo.type)
        if not strategy_cls:
            raise ValueError(f"Unsupported promo type: {vc.promo.type}")
        return strategy_cls(vc)

    @staticmethod
    def redeem_voucher(voucher_code: str, transaction_pk: int, transaction_amount: Decimal) -> Dict[str, Any]:
        """Redeem a voucher for a transaction.

        - Locks the VoucherCode row with `select_for_update()` to prevent
          concurrent redemptions.
        - Validates voucher existence and activation state.
        - Delegates calculation to the selected strategy.
        - If discount > 0, marks the voucher activated and sets reference.

        Returns a dict matching `RedeemResponseSchema`: {"voucher": VoucherCode, "calculation": {...}}
        """
        with transaction.atomic():
            vc = (
                VoucherCode.objects.select_for_update()
                .select_related("promo")
                .filter(code=voucher_code)
                .first()
            )

            if not vc:
                raise ValueError("Invalid voucher code")
            if vc.activated:
                raise ValueError("Voucher already used")

            strategy = PromoService._get_strategy_for_voucher(vc)
            calculation = strategy.calculate(transaction_amount)

            discount = calculation.get("discount") if isinstance(calculation, dict) else None
            if discount is None:
                discount = Decimal("0.00")
            # ensure Decimal
            if not isinstance(discount, Decimal):
                try:
                    discount = Decimal(str(discount))
                except Exception:
                    discount = Decimal("0.00")

            if discount > Decimal("0.00"):
                vc.activated = True
                vc.reference = transaction_pk
                vc.save()

            return {"voucher": vc, "calculation": calculation}
