from .base import BaseStrategy


class FreeShippingStrategy(BaseStrategy):
    """Strategy stub: remove fees from an order/transaction.

    Implementation to be provided by user. Methods are intentionally blank.
    """

    def calculate(self, *args, **kwargs):
        """Return computed fee removal details (stub)."""
        raise NotImplementedError()
        pass
