from abc import ABC, abstractmethod
from typing import Any
from decimal import Decimal
from apps.promoin.models import VoucherCode


class BaseStrategy(ABC):
    """Abstract base class for promo strategies.

    Concrete strategies should accept a `VoucherCode` instance in their
    constructor and implement `calculate(transaction_amount)` to return a
    dict-like calculation result (for example: {"discount": Decimal(...)}).

    Strategies should not persist voucher activation; that is the
    responsibility of the redeeming service which will perform the
    database-level locking and save the `VoucherCode` when appropriate.
    """

    def __init__(self, voucher: VoucherCode):
        if not voucher:
            raise ValueError("voucher must be provided")
        self.voucher = voucher
        self.promo = voucher.promo

    @abstractmethod
    def calculate(self, transaction_amount: Decimal) -> Any:
        """Compute the strategy result for the provided transaction amount.

        Should return a mapping that includes at least a "discount" Decimal
        value (may be Decimal("0.00")).
        """
        raise NotImplementedError()

    def redeem(self, *args, **kwargs):
        """Optional redeem hook.

        Concrete strategies may override this to perform any strategy-specific
        actions during redemption. The default implementation intentionally
        raises NotImplementedError to signal that there is no default
        persistence behaviour at the strategy level (the service layer
        handles DB updates).
        """
        raise NotImplementedError()
