from ninja import Schema
from typing import Optional


class PromoCreateSchema(Schema):
    name: str
    total_voucher: int
    type: Optional[str] = "fixed"
    amount: Optional[float] = 0.0
    min_discount: Optional[float] = 0.0
    max_discount: Optional[float] = 0.0
    min_purchase: Optional[float] = 0.0


class PromoOutSchema(Schema):
    id: int
    name: str
    total_voucher: int


class VoucherOutSchema(Schema):
    id: int
    code: str
    activated: bool
    promo_id: int


class VoucherUpdateSchema(Schema):
    activated: bool
