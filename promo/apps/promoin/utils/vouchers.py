from django.db import IntegrityError
from apps.promoin.models import VoucherCode
from libs.generators.voucher_codes import CodeGenerator


def create_voucher(promo):
    total_voucher = promo.total_voucher

    # it's already created in other session, so I will not recounting it
    if VoucherCode.objects.filter(promo=promo).exists():
        return True
   
    counter = 0
    generator = CodeGenerator()

    while counter < total_voucher:
        try:
            VoucherCode.objects.create(
                promo=promo,
                code=generator.generate(),
            )
            counter += 1
        except IntegrityError:
            # collision → retry
            continue

    return True