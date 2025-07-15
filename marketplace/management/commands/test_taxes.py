from django.core.management.base import BaseCommand
from marketplace.models import Tax
from marketplace.context_processors import calculate_dynamic_taxes
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test tax calculations with different scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subtotal',
            type=float,
            default=100.0,
            help='Subtotal amount to test'
        )
        parser.add_argument(
            '--state',
            type=str,
            help='State for location-based tax testing'
        )
        parser.add_argument(
            '--city',
            type=str,
            help='City for location-based tax testing'
        )

    def handle(self, *args, **options):
        subtotal = Decimal(str(options['subtotal']))
        user_location = {}
        
        if options['state']:
            user_location['state'] = options['state']
        if options['city']:
            user_location['city'] = options['city']

        self.stdout.write("=" * 60)
        self.stdout.write(f"TAX CALCULATION TEST")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Subtotal: ${subtotal}")
        if user_location:
            self.stdout.write(f"Location: {user_location}")
        self.stdout.write("-" * 60)

        # Test tax calculation
        result = calculate_dynamic_taxes(
            subtotal=subtotal,
            user_location=user_location if user_location else None
        )

        # Display results
        self.stdout.write("\nTAX BREAKDOWN:")
        self.stdout.write("-" * 30)
        
        if result['tax_details']:
            for tax_detail in result['tax_details']:
                self.stdout.write(
                    f"{tax_detail['name']:<20} {tax_detail['rate']:<10} ${tax_detail['amount']:>8.2f}"
                )
                if tax_detail.get('exemption_applied'):
                    self.stdout.write(
                        f"{'':20} {'Exemption:':<10} {tax_detail['exemption_percentage']}%"
                    )
        else:
            self.stdout.write("No applicable taxes found")

        self.stdout.write("-" * 50)
        self.stdout.write(f"{'Subtotal:':<30} ${subtotal:>8.2f}")
        self.stdout.write(f"{'Total Tax:':<30} ${result['total_tax']:>8.2f}")
        self.stdout.write(f"{'Grand Total:':<30} ${subtotal + result['total_tax']:>8.2f}")
        self.stdout.write("=" * 60)

        # Show active taxes
        self.stdout.write("\nACTIVE TAXES IN SYSTEM:")
        self.stdout.write("-" * 40)
        active_taxes = Tax.objects.filter(is_active=True).order_by('priority')
        
        for tax in active_taxes:
            applicable = tax.is_applicable(
                subtotal=subtotal,
                user_location=user_location if user_location else None
            )
            status = "✅ APPLICABLE" if applicable else "❌ NOT APPLICABLE"
            
            if tax.calculation_type == 'PERCENTAGE':
                rate = f"{tax.tax_percentage}%"
            else:
                rate = f"${tax.fixed_amount}"
            
            self.stdout.write(f"{tax.tax_type:<25} {rate:<10} {status}")
            
            # Show why not applicable
            if not applicable:
                reasons = []
                if tax.minimum_order_amount and subtotal < tax.minimum_order_amount:
                    reasons.append(f"Min amount: ${tax.minimum_order_amount}")
                if tax.maximum_order_amount and subtotal > tax.maximum_order_amount:
                    reasons.append(f"Max amount: ${tax.maximum_order_amount}")
                if tax.state and user_location.get('state', '').lower() != tax.state.lower():
                    reasons.append(f"State: {tax.state}")
                if tax.city and user_location.get('city', '').lower() != tax.city.lower():
                    reasons.append(f"City: {tax.city}")
                
                if reasons:
                    self.stdout.write(f"{'':25} {'':10} Reason: {', '.join(reasons)}")

        self.stdout.write("=" * 60)
