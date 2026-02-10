# promo/apps/promoout/strategies/registry.py
from typing import Type
from .base import BaseStrategy

from .discount_fixed import DiscountFixedStrategy
from .discount_percentage import DiscountPercentageStrategy
from .free_shipping import FreeShippingStrategy


STRATEGY_MAP: dict[str, Type[BaseStrategy]] = {
    "fixed": DiscountFixedStrategy,
    "percentage": DiscountPercentageStrategy,
    "free_shipping": FreeShippingStrategy,
}
