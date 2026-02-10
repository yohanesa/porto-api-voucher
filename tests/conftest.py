import pytest
import django
import os
from decimal import Decimal
from django.contrib.auth.models import User

# Configure Django settings for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promo.settings')
django.setup()

from apps.promoin.models import Promo, VoucherCode


@pytest.fixture(scope='function')
def test_user(db):
    """Create a test user."""
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture(scope='function')
def test_promo_fixed(db):
    """Create a test promo with fixed discount."""
    promo = Promo.objects.create(
        name='Fixed Discount Promo',
        type='fixed',
        total_voucher=5,
        amount=Decimal('10.00'),
        min_purchase=Decimal('50.00'),
    )
    return promo


@pytest.fixture(scope='function')
def test_promo_percentage(db):
    """Create a test promo with percentage discount."""
    promo = Promo.objects.create(
        name='Percentage Discount Promo',
        type='percentage',
        total_voucher=5,
        amount=Decimal('15.00'),
        min_purchase=Decimal('100.00'),
    )
    return promo


@pytest.fixture(scope='function')
def test_promo_free_shipping(db):
    """Create a test promo with free shipping."""
    promo = Promo.objects.create(
        name='Free Shipping Promo',
        type='free_shipping',
        total_voucher=3,
    )
    return promo


@pytest.fixture(scope='function')
def test_voucher_fixed(test_promo_fixed):
    """Create a test voucher for fixed promo."""
    voucher = VoucherCode.objects.create(
        promo=test_promo_fixed,
        code='FIXED10OFF',
        activated=False,
    )
    return voucher


@pytest.fixture(scope='function')
def test_voucher_percentage(test_promo_percentage):
    """Create a test voucher for percentage promo."""
    voucher = VoucherCode.objects.create(
        promo=test_promo_percentage,
        code='PERCENT15OFF',
        activated=False,
    )
    return voucher


@pytest.fixture(scope='function')
def test_voucher_free_shipping(test_promo_free_shipping):
    """Create a test voucher for free shipping promo."""
    voucher = VoucherCode.objects.create(
        promo=test_promo_free_shipping,
        code='FREESHIP2024',
        activated=False,
    )
    return voucher
