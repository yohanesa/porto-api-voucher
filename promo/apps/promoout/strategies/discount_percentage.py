from .base import BaseStrategy
from decimal import Decimal


class DiscountPercentageStrategy(BaseStrategy):
    """Strategy stub: apply discount to an order/transaction.

    Implementation to be provided by user. Methods are intentionally blank.
    """

    def calculate(self, transaction_amount: Decimal,  *args, **kwargs):
        """Return computed discount details (stub)."""
        if self.voucher.promo.min_purchase > transaction_amount:
            return {
                "discount": Decimal("0.00"),
                "message": "Minimum purchase amount not met for this promo.",
            }
        return {
            "discount": transaction_amount * (self.voucher.promo.amount / Decimal("100")),
            "message": "Discount applied.",
        }
