# Generated migration for user-based authorization on reservations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('promoin', '0005_vouchercode_status_pending_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='vouchercode',
            name='reserved_by_user',
            field=models.ForeignKey(
                blank=True,
                help_text='User who reserved this voucher during checkout',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reserved_vouchers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
