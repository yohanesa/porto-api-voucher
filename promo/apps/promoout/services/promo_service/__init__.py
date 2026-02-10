from decimal import Decimal
from typing import Dict, Any, Type

from django.db import transaction
from django.contrib.auth.models import User

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
                vc.status = VoucherCode.STATUS_ACTIVATED
                vc.reference = transaction_pk
                vc.save()

            return {"voucher": vc, "calculation": calculation}

    # ========== Three-Phase Payment-Dependent Redemption ==========

    @staticmethod
    def reserve_voucher(voucher_code: str, transaction_pk: int, transaction_amount: Decimal, user: User) -> Dict[str, Any]:
        """Phase 1: Reserve a voucher during checkout (before payment).

        - Locks the voucher with pessimistic locking
        - Validates promo conditions (min_purchase, strategy calculation)
        - Sets status='reserved', pending_transaction_pk, and reserved_by_user
        - Prevents other users from using this code during payment processing

        Args:
            voucher_code: The promo code string
            transaction_pk: The transaction ID from the payment system
            transaction_amount: The transaction amount for discount calculation
            user: Django User instance who is making the reservation

        Returns {"voucher": VoucherCode, "calculation": {...}} if reservation succeeds.
        Raises ValueError if voucher unavailable, calculation fails, conditions not met, or invalid user.
        """
        if not user or not user.is_authenticated:
            raise ValueError("User must be authenticated to reserve a voucher")

        with transaction.atomic():
            vc = (
                VoucherCode.objects.select_for_update()
                .select_related("promo")
                .filter(code=voucher_code)
                .first()
            )

            if not vc:
                raise ValueError(f"Invalid voucher code: {voucher_code}")

            if vc.status != VoucherCode.STATUS_AVAILABLE:
                raise ValueError(f"Voucher not available (status={vc.status})")

            # Pre-calculate to validate conditions before locking
            strategy = PromoService._get_strategy_for_voucher(vc)
            calculation = strategy.calculate(transaction_amount)

            discount = calculation.get("discount") if isinstance(calculation, dict) else None
            if discount is None:
                discount = Decimal("0.00")
            if not isinstance(discount, Decimal):
                try:
                    discount = Decimal(str(discount))
                except Exception:
                    discount = Decimal("0.00")

            if discount <= Decimal("0.00"):
                raise ValueError(f"Voucher conditions not met (discount={discount})")

            # Reserve the voucher to this user
            vc.status = VoucherCode.STATUS_RESERVED
            vc.pending_transaction_pk = transaction_pk
            vc.reserved_by_user = user
            vc.save()

            return {"voucher": vc, "calculation": calculation}

    @staticmethod
    def confirm_redemption(voucher_code: str, transaction_pk: int, user: User) -> VoucherCode:
        """Phase 2: Confirm redemption after payment succeeds.

        - Locks the voucher
        - Validates it was previously reserved with matching transaction_pk
        - Verifies that only the user who reserved it can confirm
        - Transitions status='reserved' → status='activated'
        - Sets final reference and clears pending_transaction_pk

        Args:
            voucher_code: The promo code string
            transaction_pk: The transaction ID (must match the reserved transaction)
            user: Django User instance confirming the redemption

        Raises ValueError if voucher not found, not in reserved state, txn_pk mismatch, or unauthorized user.
        """
        if not user or not user.is_authenticated:
            raise ValueError("User must be authenticated to confirm redemption")

        with transaction.atomic():
            vc = (
                VoucherCode.objects.select_for_update()
                .filter(code=voucher_code)
                .first()
            )

            if not vc:
                raise ValueError(f"Invalid voucher code: {voucher_code}")

            if vc.status != VoucherCode.STATUS_RESERVED:
                raise ValueError(
                    f"Voucher not in reserved state (status={vc.status}). "
                    f"Cannot confirm redemption."
                )

            if vc.pending_transaction_pk != transaction_pk:
                raise ValueError(
                    f"Transaction mismatch. Expected {vc.pending_transaction_pk}, "
                    f"got {transaction_pk}."
                )

            # Verify authorization: only the user who reserved can confirm
            if vc.reserved_by_user_id != user.id:
                raise ValueError(
                    f"Unauthorized: only the user who reserved this voucher "
                    f"(user_id={vc.reserved_by_user_id}) can confirm redemption. "
                    f"Current user: {user.id}"
                )

            # Confirm and finalize
            vc.status = VoucherCode.STATUS_ACTIVATED
            vc.activated = True  # backward compatibility
            vc.reference = transaction_pk
            vc.pending_transaction_pk = None
            vc.save()

            return vc

    @staticmethod
    def rollback_reservation(voucher_code: str, transaction_pk: int, user: User) -> VoucherCode:
        """Phase 3: Rollback reservation if payment fails or is canceled.

        - Locks the voucher
        - Validates it was reserved with matching transaction_pk
        - Verifies that only the user who reserved it can rollback
        - Transitions status='reserved' → status='available'
        - Clears pending_transaction_pk and reserved_by_user

        Args:
            voucher_code: The promo code string
            transaction_pk: The transaction ID (must match the reserved transaction)
            user: Django User instance requesting the rollback

        Raises ValueError if voucher not found, not reserved, txn_pk mismatch, or unauthorized user.
        """
        if not user or not user.is_authenticated:
            raise ValueError("User must be authenticated to rollback reservation")

        with transaction.atomic():
            vc = (
                VoucherCode.objects.select_for_update()
                .filter(code=voucher_code)
                .first()
            )

            if not vc:
                raise ValueError(f"Invalid voucher code: {voucher_code}")

            if vc.status != VoucherCode.STATUS_RESERVED:
                raise ValueError(
                    f"Voucher not in reserved state (status={vc.status}). "
                    f"Cannot rollback."
                )

            if vc.pending_transaction_pk != transaction_pk:
                raise ValueError(
                    f"Transaction mismatch. Expected {vc.pending_transaction_pk}, "
                    f"got {transaction_pk}."
                )

            # Verify authorization: only the user who reserved can rollback
            if vc.reserved_by_user_id != user.id:
                raise ValueError(
                    f"Unauthorized: only the user who reserved this voucher "
                    f"(user_id={vc.reserved_by_user_id}) can rollback. "
                    f"Current user: {user.id}"
                )

            # Release the hold
            vc.status = VoucherCode.STATUS_AVAILABLE
            vc.pending_transaction_pk = None
            vc.reserved_by_user = None
            vc.save()

            return vc

