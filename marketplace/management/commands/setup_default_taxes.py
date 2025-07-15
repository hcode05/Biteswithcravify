from django.core.management.base import BaseCommand
from marketplace.models import Tax


class Command(BaseCommand):
    help = 'Add default tax types'

    def handle(self, *args, **options):
        # Default taxes to create
        default_taxes = [
            {'tax_type': 'Sales Tax', 'tax_percentage': 8.50},
            {'tax_type': 'VAT', 'tax_percentage': 15.00},
            {'tax_type': 'Service Tax', 'tax_percentage': 5.00},
            {'tax_type': 'Delivery Tax', 'tax_percentage': 2.00},
        ]
        
        created_count = 0
        for tax_data in default_taxes:
            tax, created = Tax.objects.get_or_create(
                tax_type=tax_data['tax_type'],
                defaults={
                    'tax_percentage': tax_data['tax_percentage'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created tax: {tax.tax_type} ({tax.tax_percentage}%)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'✓ Tax already exists: {tax.tax_type} ({tax.tax_percentage}%)')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Successfully created {created_count} new tax types!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ All default taxes already exist!')
            )
        
        self.stdout.write('\nYou can now:')
        self.stdout.write('• Go to Admin Panel → Marketplace → Taxes')
        self.stdout.write('• Add/Edit tax types and percentages')
        self.stdout.write('• Enable/Disable taxes as needed')
