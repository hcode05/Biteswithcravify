# Generated manually to add missing columns to Tax model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_tax'),
    ]

    operations = [
        migrations.AddField(
            model_name='tax',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tax',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='tax',
            name='tax_type',
            field=models.CharField(max_length=50, unique=True, help_text="e.g., Sales Tax, VAT, Service Tax"),
        ),
        migrations.AlterField(
            model_name='tax',
            name='tax_percentage',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Tax Percentage (%)', help_text="Enter percentage (e.g., 8.5 for 8.5%)"),
        ),
        migrations.AlterModelOptions(
            name='tax',
            options={'ordering': ['tax_type'], 'verbose_name': 'Tax', 'verbose_name_plural': 'Taxes'},
        ),
    ]
