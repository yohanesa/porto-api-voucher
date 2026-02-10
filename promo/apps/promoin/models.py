from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from libs.basemodel import BaseModel

class Promo(BaseModel):
    name = models.CharField(max_length=128)
    total_voucher = models.IntegerField(default=1, validators=[
            MinValueValidator(1),
            MaxValueValidator(10000),
        ])

    PROMO_TYPE_PERCENTAGE = "percentage"
    PROMO_TYPE_FIXED = "fixed"
    PROMO_TYPE_FREE_SHIPPING = "free_shipping"
    PROMO_TYPE_CHOICES = (
        (PROMO_TYPE_PERCENTAGE, "Percentage"),
        (PROMO_TYPE_FIXED, "Fixed amount"),
        (PROMO_TYPE_FREE_SHIPPING, "Free shipping"),
    )

    type = models.CharField(max_length=32, choices=PROMO_TYPE_CHOICES, default=PROMO_TYPE_FIXED)
    # amount can be percentage or fixed amount based on type
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # if min purchase is set, promo is applicable only for orders above this amount
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class VoucherCode(BaseModel):
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE)
    code = models.CharField(max_length=128, unique=True)
    
    STATUS_AVAILABLE = 'available'
    STATUS_RESERVED = 'reserved'  # Locked during payment processing
    STATUS_ACTIVATED = 'activated'  # Fully redeemed
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_RESERVED, 'Reserved (pending payment)'),
        (STATUS_ACTIVATED, 'Activated (redeemed)'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )
    
    # For backward compatibility
    activated = models.BooleanField(default=False)
    
    # Temporary hold during reservation phase (pending payment confirmation)
    pending_transaction_pk = models.BigIntegerField(blank=True, null=True)
    
    # User who reserved the voucher (for authorization)
    reserved_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_vouchers',
        help_text='User who reserved this voucher during checkout'
    )
    
    # Final reference after confirmation
    reference = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} ({self.promo})"