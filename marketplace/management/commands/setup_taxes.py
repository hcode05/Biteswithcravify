from django.core.management.base import BaseCommand
from marketplace.models import Tax, TaxCategory
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up common tax configurations for the dynamic tax system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--country',
            type=str,
            default='US',
            help='Country code for tax setup (US, IN, UK, etc.)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing tax configurations'
        )

    def handle(self, *args, **options):
        country = options['country'].upper()
        
        if options['clear_existing']:
            self.stdout.write("Clearing existing tax configurations...")
            Tax.objects.all().delete()
            TaxCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing taxes"))

        self.stdout.write(f"Setting up taxes for country: {country}")
        
        if country == 'US':
            self.setup_us_taxes()
        elif country == 'IN':
            self.setup_indian_taxes()
        elif country == 'UK':
            self.setup_uk_taxes()
        else:
            self.setup_generic_taxes()
        
        self.stdout.write(self.style.SUCCESS("Tax setup completed successfully!"))

    def setup_us_taxes(self):
        """Setup US tax structure"""
        # Create tax categories
        federal_cat, _ = TaxCategory.objects.get_or_create(
            name="Federal Taxes",
            defaults={'description': 'Federal level taxes'}
        )
        state_cat, _ = TaxCategory.objects.get_or_create(
            name="State Taxes", 
            defaults={'description': 'State level taxes'}
        )
        local_cat, _ = TaxCategory.objects.get_or_create(
            name="Local Taxes",
            defaults={'description': 'City and county level taxes'}
        )

        # Create common US taxes
        taxes = [
            {
                'tax_type': 'Sales Tax - California',
                'tax_category': state_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('7.75'),
                'state': 'California',
                'description': 'California state sales tax'
            },
            {
                'tax_type': 'Sales Tax - New York',
                'tax_category': state_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('8.00'),
                'state': 'New York',
                'description': 'New York state sales tax'
            },
            {
                'tax_type': 'Service Fee',
                'tax_category': local_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('3.00'),
                'applicability': 'ALL',
                'description': 'Service and handling fee'
            }
        ]
        
        for tax_data in taxes:
            tax, created = Tax.objects.get_or_create(
                tax_type=tax_data['tax_type'],
                defaults=tax_data
            )
            if created:
                self.stdout.write(f"Created: {tax.tax_type}")

    def setup_indian_taxes(self):
        """Setup Indian GST structure"""
        gst_cat, _ = TaxCategory.objects.get_or_create(
            name="GST",
            defaults={'description': 'Goods and Services Tax'}
        )

        taxes = [
            {
                'tax_type': 'CGST',
                'tax_category': gst_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('9.00'),
                'description': 'Central GST for food delivery (18% split as 9% CGST + 9% SGST)'
            },
            {
                'tax_type': 'SGST',
                'tax_category': gst_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('9.00'),
                'description': 'State GST for food delivery'
            },
            {
                'tax_type': 'Delivery Charges GST',
                'tax_category': gst_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('5.00'),
                'minimum_order_amount': Decimal('0.01'),
                'description': 'GST on delivery charges'
            }
        ]

        for tax_data in taxes:
            tax, created = Tax.objects.get_or_create(
                tax_type=tax_data['tax_type'],
                defaults=tax_data
            )
            if created:
                self.stdout.write(f"Created: {tax.tax_type}")

    def setup_uk_taxes(self):
        """Setup UK VAT structure"""
        vat_cat, _ = TaxCategory.objects.get_or_create(
            name="VAT",
            defaults={'description': 'Value Added Tax'}
        )

        taxes = [
            {
                'tax_type': 'Standard VAT',
                'tax_category': vat_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('20.00'),
                'description': 'Standard UK VAT rate'
            },
            {
                'tax_type': 'Service Charge',
                'tax_category': vat_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('2.50'),
                'description': 'Service charge for food delivery'
            }
        ]

        for tax_data in taxes:
            tax, created = Tax.objects.get_or_create(
                tax_type=tax_data['tax_type'],
                defaults=tax_data
            )
            if created:
                self.stdout.write(f"Created: {tax.tax_type}")

    def setup_generic_taxes(self):
        """Setup generic tax structure"""
        general_cat, _ = TaxCategory.objects.get_or_create(
            name="General Taxes",
            defaults={'description': 'General tax category'}
        )

        taxes = [
            {
                'tax_type': 'Sales Tax',
                'tax_category': general_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('8.00'),
                'description': 'General sales tax'
            },
            {
                'tax_type': 'Service Fee',
                'tax_category': general_cat,
                'calculation_type': 'PERCENTAGE',
                'tax_percentage': Decimal('2.00'),
                'description': 'Service fee'
            },
            {
                'tax_type': 'Delivery Fee',
                'tax_category': general_cat,
                'calculation_type': 'FIXED',
                'fixed_amount': Decimal('2.50'),
                'description': 'Fixed delivery fee'
            }
        ]

        for tax_data in taxes:
            tax, created = Tax.objects.get_or_create(
                tax_type=tax_data['tax_type'],
                defaults=tax_data
            )
            if created:
                self.stdout.write(f"Created: {tax.tax_type}")
