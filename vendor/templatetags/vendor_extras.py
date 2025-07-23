from django import template

register = template.Library()

try:
    from orders.utils import order_total_by_vendor

    @register.filter
    def order_total_by_vendor_filter(order, vendor_id):
        """Template filter to calculate order total for a specific vendor"""
        return order_total_by_vendor(order, vendor_id)
except Exception as e:
    print("Error importing order_total_by_vendor:", e)

@register.filter
def test_filter(value):
    """A simple test filter that returns 'OK' regardless of input."""
    return "OK" 