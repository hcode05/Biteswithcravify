import json

# Test JSON serialization
test_data = {
    'subtotal': 25.99,
    'tax': 3.90,
    'grand_total': 29.89,
    'tax_dict': {'CGST': {'9.0': 2.34}, 'SGST': {'6.0': 1.56}}
}

try:
    result = json.dumps(test_data)
    print("✓ JSON serialization works")
    print("Result:", result)
except Exception as e:
    print("❌ JSON Error:", str(e))
