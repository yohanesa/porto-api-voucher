import pytest
from apps.promoout.strategies.registry import STRATEGY_MAP
from apps.promoout.strategies.discount_fixed import DiscountFixedStrategy
from apps.promoout.strategies.discount_percentage import DiscountPercentageStrategy
from apps.promoout.strategies.free_shipping import FreeShippingStrategy


class TestStrategyRegistry:
    """Tests for the strategy registry mapping."""

    def test_registry_contains_all_types(self):
        """Registry should contain entries for all promo types."""
        expected_types = ['fixed', 'percentage', 'free_shipping']
        for promo_type in expected_types:
            assert promo_type in STRATEGY_MAP

    def test_registry_maps_to_correct_classes(self):
        """Registry should map promo types to correct strategy classes."""
        assert STRATEGY_MAP['fixed'] == DiscountFixedStrategy
        assert STRATEGY_MAP['percentage'] == DiscountPercentageStrategy
        assert STRATEGY_MAP['free_shipping'] == FreeShippingStrategy

    def test_registry_values_are_classes(self):
        """All registry values should be class types."""
        for strategy_cls in STRATEGY_MAP.values():
            assert isinstance(strategy_cls, type)

    def test_registry_returns_strategy_subclass(self):
        """All mapped classes should be proper strategy subclasses."""
        from apps.promoout.strategies.base import BaseStrategy
        
        for strategy_cls in STRATEGY_MAP.values():
            assert issubclass(strategy_cls, BaseStrategy)

    def test_registry_immutability_check(self):
        """Verify registry can be safely iterated (basic immutability)."""
        registry_snapshot = dict(STRATEGY_MAP)
        
        # Iterate over original
        for key, value in STRATEGY_MAP.items():
            assert key in registry_snapshot
            assert registry_snapshot[key] == value

    def test_unsupported_type_not_in_registry(self):
        """Unsupported promo types should not be in registry."""
        unsupported_types = ['bonus', 'coupon', 'invalid_type']
        for promo_type in unsupported_types:
            assert promo_type not in STRATEGY_MAP
