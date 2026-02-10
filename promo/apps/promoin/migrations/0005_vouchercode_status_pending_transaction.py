# Generated migration for three-phase payment-dependent redemption

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promoin', '0004_promo_amount_promo_max_discount_promo_min_discount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vouchercode',
            name='status',
            field=models.CharField(
                choices=[
                    ('available', 'Available'),
                    ('reserved', 'Reserved (pending payment)'),
                    ('activated', 'Activated (redeemed)'),
                ],
                default='available',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='vouchercode',
            name='pending_transaction_pk',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
