from ninja import Schema
from typing import Optional, Dict, Any


class RedeemSchema(Schema):
    """Payload to redeem a voucher code.

    code: the voucher code string
    transaction_pk: unique identifier for the transaction
    transaction_amount: the transaction amount to apply discount against
    """
    code: str
    transcation_pk: int
    transaction_amount: float


class CalculationResultSchema(Schema):
    """Calculation result from strategy.

    discount: discount amount calculated by the strategy
    fee_removed: optional fee removal amount
    details: optional additional calculation details
    """
    discount: float
    message: Optional[Dict[str, Any]] = None


class VoucherRedeemSchema(Schema):
    """Voucher details in redemption response.

    id: voucher id
    code: voucher code
    activated: activation status
    reference: transaction reference (e.g., transaction_pk)
    """
    id: int
    code: str
    activated: bool
    reference: Optional[int] = None


class RedeemResponseSchema(Schema):
    """Response schema for voucher redemption.

    voucher: the redeemed voucher with updated status
    calculation: calculation result from the applied strategy
    """
    voucher: VoucherRedeemSchema
    calculation: CalculationResultSchema
