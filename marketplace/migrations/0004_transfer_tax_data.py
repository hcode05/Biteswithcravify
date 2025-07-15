# Data migration to transfer old tax data to new dynamic tax system

from django.db import migrations


def transfer_tax_data(apps, schema_editor):
    """Transfer data from old Tax model to new dynamic tax models"""
    TaxOld = apps.get_model('marketplace', 'TaxOld')
    TaxCategory = apps.get_model('marketplace', 'TaxCategory')
    Tax = apps.get_model('marketplace', 'Tax')
    
    # Create default tax categories
    sales_tax_category, _ = TaxCategory.objects.get_or_create(
        name='Sales Tax',
        defaults={
            'description': 'Standard sales tax applied to most items',
            'is_active': True
        }
    )
    
    service_tax_category, _ = TaxCategory.objects.get_or_create(
        name='Service Tax',
        defaults={
            'description': 'Tax applied to services and delivery',
            'is_active': True
        }
    )
    
    # Transfer existing tax data
    for old_tax in TaxOld.objects.all():
        # Determine category based on tax_type
        if 'service' in old_tax.tax_type.lower():
            category = service_tax_category
        else:
            category = sales_tax_category
            
        Tax.objects.create(
            name=old_tax.tax_type,
            rate=old_tax.tax_percentage,
            calculation_type='percentage',
            category=category,
            is_active=old_tax.is_active,
            applicable_on='subtotal',
            priority=1
        )


def reverse_transfer_tax_data(apps, schema_editor):
    """Reverse the data transfer if needed"""
    # This is a safety measure - in case we need to rollback
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_dynamic_tax_system'),
    ]

    operations = [
        migrations.RunPython(transfer_tax_data, reverse_transfer_tax_data),
    ]
