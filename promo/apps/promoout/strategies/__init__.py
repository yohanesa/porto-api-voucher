"""Strategies package for promoout.

Exports common strategy classes for convenience.
"""

from .base import BaseStrategy
from .free_shipping import FreeShippingStrategy
from .discount_fixed import DiscountFixedStrategy
from .discount_percentage import DiscountPercentageStrategy

__all__ = [
    "BaseStrategy",
    "RemoveFeesStrategy",
    "DiscountFixedStrategy",
    "DiscountPercentageStrategy",
]
