import pytest
from decimal import Decimal
from apps.promoout.strategies.discount_fixed import DiscountFixedStrategy
from apps.promoout.strategies.discount_percentage import DiscountPercentageStrategy
from apps.promoout.strategies.free_shipping import FreeShippingStrategy


class TestDiscountFixedStrategy:
    """Unit tests for DiscountFixedStrategy."""

    def test_calculate_fixed_discount_below_min_purchase(self, test_voucher_fixed):
        """Fixed discount should return 0 if transaction below min_purchase."""
        strategy = DiscountFixedStrategy(test_voucher_fixed)
        result = strategy.calculate(Decimal('30.00'))  # Below min_purchase of 50
        
        assert result['discount'] == Decimal('0.00')
        assert 'message' in result

    def test_calculate_fixed_discount_meets_min_purchase(self, test_voucher_fixed):
        """Fixed discount should apply if transaction meets min_purchase."""
        strategy = DiscountFixedStrategy(test_voucher_fixed)
        result = strategy.calculate(Decimal('100.00'))  # Above min_purchase of 50
        
        assert result['discount'] == Decimal('10.00')
        assert 'message' in result

    def test_fixed_strategy_returns_dict(self, test_voucher_fixed):
        """Strategy calculate should always return a dict with discount key."""
        strategy = DiscountFixedStrategy(test_voucher_fixed)
        result = strategy.calculate(Decimal('50.00'))
        
        assert isinstance(result, dict)
        assert 'discount' in result
        assert isinstance(result['discount'], Decimal)


class TestDiscountPercentageStrategy:
    """Unit tests for DiscountPercentageStrategy."""

    def test_calculate_percentage_discount_below_min_purchase(self, test_voucher_percentage):
        """Percentage discount should return 0 if transaction below min_purchase."""
        strategy = DiscountPercentageStrategy(test_voucher_percentage)
        result = strategy.calculate(Decimal('50.00'))  # Below min_purchase of 100
        
        assert result['discount'] == Decimal('0.00')
        assert 'message' in result

    def test_calculate_percentage_discount_meets_min_purchase(self, test_voucher_percentage):
        """Percentage discount should calculate correctly if transaction meets min_purchase."""
        strategy = DiscountPercentageStrategy(test_voucher_percentage)
        # 15% of 200 = 30
        result = strategy.calculate(Decimal('200.00'))
        
        expected_discount = Decimal('200.00') * (Decimal('15.00') / Decimal('100'))
        assert result['discount'] == expected_discount
        assert 'message' in result

    def test_percentage_strategy_precision(self, test_voucher_percentage):
        """Percentage discount should maintain Decimal precision."""
        strategy = DiscountPercentageStrategy(test_voucher_percentage)
        result = strategy.calculate(Decimal('333.33'))
        
        assert isinstance(result['discount'], Decimal)
        # 15% of 333.33
        expected = Decimal('333.33') * (Decimal('15') / Decimal('100'))
        assert result['discount'] == expected


class TestFreeShippingStrategy:
    """Unit tests for FreeShippingStrategy."""

    def test_free_shipping_strategy_exists(self, test_voucher_free_shipping):
        """FreeShippingStrategy should instantiate."""
        strategy = FreeShippingStrategy(test_voucher_free_shipping)
        assert strategy is not None

    def test_free_shipping_has_calculate_method(self, test_voucher_free_shipping):
        """FreeShippingStrategy should have calculate method."""
        strategy = FreeShippingStrategy(test_voucher_free_shipping)
        assert hasattr(strategy, 'calculate')
        assert callable(getattr(strategy, 'calculate'))


class TestStrategyInheritance:
    """Test that all strategies properly inherit from BaseStrategy."""

    def test_all_strategies_have_required_methods(self, test_voucher_fixed):
        """All strategy classes should have required methods."""
        strategies = [
            DiscountFixedStrategy(test_voucher_fixed),
            DiscountPercentageStrategy(test_voucher_fixed),
            FreeShippingStrategy(test_voucher_fixed),
        ]
        
        for strategy in strategies:
            assert hasattr(strategy, 'calculate')
            assert hasattr(strategy, 'redeem')
            assert callable(strategy.calculate)
            assert callable(strategy.redeem)

    def test_strategy_has_voucher_and_promo_attributes(self, test_voucher_fixed):
        """All strategies should have voucher and promo attributes."""
        strategy = DiscountFixedStrategy(test_voucher_fixed)
        
        assert hasattr(strategy, 'voucher')
        assert hasattr(strategy, 'promo')
        assert strategy.voucher == test_voucher_fixed
        assert strategy.promo == test_voucher_fixed.promo
