# Cleanup migration to remove old tax model after successful data transfer

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_transfer_tax_data'),
    ]

    operations = [
        # Remove the old tax model after successful data transfer
        migrations.DeleteModel(
            name='TaxOld',
        ),
    ]
