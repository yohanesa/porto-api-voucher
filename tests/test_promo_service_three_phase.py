import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from apps.promoout.services.promo_service import PromoService
from apps.promoin.models import VoucherCode


class TestPromoServiceThreePhaseRedemption:
    """Tests for three-phase payment-dependent voucher redemption with user authorization."""

    @pytest.fixture
    def auth_user(self, db):
        """Create an authenticated test user."""
        return User.objects.create_user(username='testuser', password='testpass123')

    @pytest.fixture
    def other_user(self, db):
        """Create another test user for authorization tests."""
        return User.objects.create_user(username='otheruser', password='otherpass123')

    def test_reserve_voucher_success(self, test_voucher_fixed, auth_user):
        """Reserve should lock voucher and set status=reserved with user tracking."""
        result = PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        assert 'voucher' in result
        assert 'calculation' in result
        assert result['voucher'].status == VoucherCode.STATUS_RESERVED
        assert result['voucher'].pending_transaction_pk == 100
        assert result['voucher'].reserved_by_user_id == auth_user.id
        assert result['calculation']['discount'] == Decimal('10.00')

    def test_reserve_voucher_unauthenticated(self, test_voucher_fixed):
        """Reserve should fail for unauthenticated users."""
        with pytest.raises(ValueError, match="must be authenticated"):
            PromoService.reserve_voucher(
                voucher_code=test_voucher_fixed.code,
                transaction_pk=100,
                transaction_amount=Decimal('100.00'),
                user=None,
            )

    def test_confirm_redemption_success(self, test_voucher_fixed, auth_user):
        """Confirm should transition reserved → activated and set final reference."""
        # Phase 1: Reserve
        PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        # Phase 2: Confirm
        vc = PromoService.confirm_redemption(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            user=auth_user,
        )

        assert vc.status == VoucherCode.STATUS_ACTIVATED
        assert vc.activated is True
        assert vc.reference == 100
        assert vc.pending_transaction_pk is None

    def test_confirm_redemption_unauthorized_user(self, test_voucher_fixed, auth_user, other_user):
        """Confirm should fail if different user tries to confirm."""
        # Phase 1: Reserve by auth_user
        PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        # Phase 2: Try to confirm as different user
        with pytest.raises(ValueError, match="Unauthorized"):
            PromoService.confirm_redemption(
                voucher_code=test_voucher_fixed.code,
                transaction_pk=100,
                user=other_user,
            )

    def test_confirm_redemption_unauthenticated(self, test_voucher_fixed, auth_user):
        """Confirm should fail for unauthenticated users."""
        # Phase 1: Reserve
        PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        # Phase 2: Try to confirm without auth
        with pytest.raises(ValueError, match="must be authenticated"):
            PromoService.confirm_redemption(
                voucher_code=test_voucher_fixed.code,
                transaction_pk=100,
                user=None,
            )

    def test_rollback_reservation_success(self, test_voucher_fixed, auth_user):
        """Rollback should transition reserved → available."""
        # Phase 1: Reserve
        PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        # Phase 3: Rollback
        vc = PromoService.rollback_reservation(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            user=auth_user,
        )

        assert vc.status == VoucherCode.STATUS_AVAILABLE
        assert vc.pending_transaction_pk is None
        assert vc.reserved_by_user is None
        assert vc.reference is None

    def test_rollback_reservation_unauthorized_user(self, test_voucher_fixed, auth_user, other_user):
        """Rollback should fail if different user tries to rollback."""
        # Phase 1: Reserve by auth_user
        PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        # Phase 3: Try to rollback as different user
        with pytest.raises(ValueError, match="Unauthorized"):
            PromoService.rollback_reservation(
                voucher_code=test_voucher_fixed.code,
                transaction_pk=100,
                user=other_user,
            )

    def test_rollback_reservation_unauthenticated(self, test_voucher_fixed, auth_user):
        """Rollback should fail for unauthenticated users."""
        # Phase 1: Reserve
        PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=100,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )

        # Phase 3: Try to rollback without auth
        with pytest.raises(ValueError, match="must be authenticated"):
            PromoService.rollback_reservation(
                voucher_code=test_voucher_fixed.code,
                transaction_pk=100,
                user=None,
            )

    def test_full_flow_reserve_confirm(self, test_voucher_fixed, auth_user):
        """Full happy path: reserve → confirm with same user."""
        txn_pk = 42

        # Phase 1: Reserve during checkout
        reserve_result = PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=txn_pk,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )
        assert reserve_result['voucher'].status == VoucherCode.STATUS_RESERVED

        # Phase 2: Confirm after payment succeeds
        confirmed_vc = PromoService.confirm_redemption(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=txn_pk,
            user=auth_user,
        )
        assert confirmed_vc.status == VoucherCode.STATUS_ACTIVATED
        assert confirmed_vc.reference == txn_pk

        # Verify from DB
        test_voucher_fixed.refresh_from_db()
        assert test_voucher_fixed.status == VoucherCode.STATUS_ACTIVATED
        assert test_voucher_fixed.reference == txn_pk

    def test_full_flow_reserve_rollback(self, test_voucher_fixed, auth_user):
        """Full happy path: reserve → rollback with same user."""
        txn_pk = 42

        # Phase 1: Reserve during checkout
        reserve_result = PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=txn_pk,
            transaction_amount=Decimal('100.00'),
            user=auth_user,
        )
        assert reserve_result['voucher'].status == VoucherCode.STATUS_RESERVED

        # Phase 3: Rollback if payment fails
        rolled_back_vc = PromoService.rollback_reservation(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=txn_pk,
            user=auth_user,
        )
        assert rolled_back_vc.status == VoucherCode.STATUS_AVAILABLE

        # Verify from DB and that voucher is available again
        test_voucher_fixed.refresh_from_db()
        assert test_voucher_fixed.status == VoucherCode.STATUS_AVAILABLE

        # Now another user should be able to reserve
        other_user = User.objects.create_user(username='newuser', password='newpass123')
        reserve_result2 = PromoService.reserve_voucher(
            voucher_code=test_voucher_fixed.code,
            transaction_pk=999,
            transaction_amount=Decimal('100.00'),
            user=other_user,
        )
        assert reserve_result2['voucher'].status == VoucherCode.STATUS_RESERVED
        assert reserve_result2['voucher'].pending_transaction_pk == 999
        assert reserve_result2['voucher'].reserved_by_user_id == other_user.id
