from django.db import models
from libs.basemodel import BaseModel
from apps.promoin.models import VoucherCode


class RedeemVoucher(BaseModel):
    code = models.ForeignKey(VoucherCode, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.IntegerField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"RedeemVoucher for {self.code}"