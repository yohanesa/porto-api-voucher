from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Promo
from .utils.vouchers import create_voucher


@receiver(post_save, sender=Promo)
def create_vouchers_on_promo_created(sender, instance, created, **kwargs):
    # create_voucher reads instance.total_voucher internally
    create_voucher(instance)
