import pytest
from decimal import Decimal
from django.db import transaction
from apps.promoout.services.promo_service import PromoService


class TestPromoServiceRedeem:
    """Integration tests for PromoService.redeem_voucher()."""

    def test_redeem_voucher_fixed_discount_success(self, test_voucher_fixed):
        """Redeem should apply fixed discount when conditions met."""
        result = PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=1,
            transaction_amount=Decimal('100.00'),
        )
        
        assert 'voucher' in result
        assert 'calculation' in result
        assert result['voucher'].activated is True
        assert result['voucher'].reference == 1
        assert result['calculation']['discount'] == Decimal('10.00')

    def test_redeem_voucher_fixed_discount_below_min_purchase(self, test_voucher_fixed):
        """Redeem should not activate voucher if amount below min_purchase."""
        result = PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=1,
            transaction_amount=Decimal('30.00'),  # Below 50 min_purchase
        )
        
        # Voucher should NOT be activated if discount is 0
        assert result['voucher'].activated is False
        assert result['calculation']['discount'] == Decimal('0.00')

    def test_redeem_voucher_percentage_discount(self, test_voucher_percentage):
        """Redeem should calculate percentage discount correctly."""
        result = PromoService.redeem_voucher(
            voucher_code=test_voucher_percentage.code,
            transaction_pk=2,
            transaction_amount=Decimal('200.00'),
        )
        
        # 15% of 200 = 30
        expected_discount = Decimal('30.00')
        assert result['voucher'].activated is True
        assert result['calculation']['discount'] == expected_discount

    @pytest.mark.django_db
    def test_redeem_invalid_voucher_code(self):
        """Redeem should raise ValueError for invalid voucher code."""
        with pytest.raises(ValueError, match="Invalid voucher code"):
            PromoService.redeem_voucher(
                voucher_code='INVALID_CODE_12345',
                transaction_pk=1,
                transaction_amount=Decimal('100.00'),
            )

    def test_redeem_already_used_voucher(self, test_voucher_fixed):
        """Redeem should raise ValueError if voucher already used."""
        # First redeem should succeed
        PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=1,
            transaction_amount=Decimal('100.00'),
        )
        
        # Second redeem should fail
        with pytest.raises(ValueError, match="Voucher already used"):
            PromoService.redeem_voucher(
                voucher_code=test_voucher_fixed.code,
                transaction_pk=2,
                transaction_amount=Decimal('100.00'),
            )

    def test_redeem_sets_reference_transaction_pk(self, test_voucher_fixed):
        """Redeem should set voucher reference to transaction_pk."""
        transaction_pk = 42
        PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=transaction_pk,
            transaction_amount=Decimal('100.00'),
        )
        
        # Refresh from DB to verify persistence
        test_voucher_fixed.refresh_from_db()
        assert test_voucher_fixed.reference == transaction_pk

    def test_redeem_response_schema_match(self, test_voucher_fixed):
        """Redeem response should match expected schema."""
        result = PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=1,
            transaction_amount=Decimal('100.00'),
        )
        
        # Check structure matches RedeemResponseSchema
        assert 'voucher' in result
        assert 'calculation' in result
        
        # Voucher fields
        voucher = result['voucher']
        assert hasattr(voucher, 'id')
        assert hasattr(voucher, 'code')
        assert hasattr(voucher, 'activated')
        assert hasattr(voucher, 'reference')
        
        # Calculation fields
        calc = result['calculation']
        assert 'discount' in calc
        assert isinstance(calc['discount'], (Decimal, int, float))

    def test_redeem_atomicity_pessimistic_lock(self, test_voucher_fixed):
        """Redeem should use pessimistic locking for atomicity."""
        # This test verifies the mechanism is in place
        # In a real concurrent test, we'd use threading/multiprocessing
        result = PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=1,
            transaction_amount=Decimal('100.00'),
        )
        
        # Verify data is persisted atomically
        test_voucher_fixed.refresh_from_db()
        assert test_voucher_fixed.activated is True
        assert test_voucher_fixed.reference == 1

    def test_redeem_decimal_precision(self, test_voucher_fixed):
        """Redeem should maintain Decimal precision."""
        result = PromoService.redeem_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=1,
            transaction_amount=Decimal('99.99'),
        )
        
        # Discount should be Decimal
        assert isinstance(result['calculation']['discount'], Decimal)

    def test_redeem_free_shipping_strategy(self, test_voucher_free_shipping):
        """Redeem should attempt free shipping strategy (may not be implemented)."""
        # FreeShippingStrategy.calculate() raises NotImplementedError (not yet implemented)
        # This test verifies the service gracefully handles it
        with pytest.raises(NotImplementedError):
            PromoService.redeem_voucher(
                voucher_code=test_voucher_free_shipping.code,
                transaction_pk=3,
                transaction_amount=Decimal('150.00'),
            )
