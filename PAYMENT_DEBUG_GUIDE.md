## Payment Debug Checklist

### Issue: Orders created but Payments missing

### What we fixed:
1. **AJAX Header Issue** - Added explicit `X-Requested-With: XMLHttpRequest` header
2. **Request Validation** - Relaxed validation to accept any POST request (not just AJAX)
3. **CSRF Protection** - Added @csrf_exempt decorator to payments view
4. **Enhanced Error Logging** - Added comprehensive debug output
5. **Better Error Handling** - Specific try-catch blocks for order lookup

### Test Steps:

1. **Check Server Console**: Look for these debug messages when payment is attempted:
   ```
   DEBUG: Payment request received - Method: POST
   DEBUG: Headers: {...}
   DEBUG: POST data: {...}
   DEBUG: Processing payment for order ORDER_NUMBER
   DEBUG: Found order ORDER_NUMBER for user EMAIL
   DEBUG: Payment created with ID: X, Amount: Y
   DEBUG: Order saved - Status: Accepted, Is Ordered: True
   ```

2. **Browser Console**: Check for JavaScript errors and AJAX responses:
   ```javascript
   // Should see:
   Payment response received: {success: true, order_number: "...", ...}
   // NOT:
   AJAX Error Details: {...}
   ```

3. **Database Check**: After payment attempt, check:
   - Orders table: Should have order with is_ordered=True, status='Accepted'
   - Payments table: Should have payment record with correct transaction_id
   - OrderedFood table: Should have food items linked to order and payment

### Common Issues:
- **CSRF Token**: Make sure CSRF token is being sent correctly
- **User Authentication**: Ensure user is logged in when making payment
- **Order Ownership**: Order must belong to the logged-in user
- **PayPal Status**: Must be "COMPLETED" for successful payment

### Quick Test Command:
```python
# In Django shell:
from orders.models import Order, Payment
print("Orders:", Order.objects.count())
print("Payments:", Payment.objects.count())
# Should match after successful payment
```
