from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    activated = models.BooleanField(default=False)
    reference = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} ({self.promo})"