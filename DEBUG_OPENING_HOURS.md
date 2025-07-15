# Opening Hours Debug Guide

## Quick Fix Steps:

### 1. **Add Debug Script (DONE)**
The debug script is now included in your opening_hours.html template.

### 2. **Test Now**
1. Go to your opening hours page: `http://localhost:8000/vendor/opening-hours/`
2. Open Browser Developer Tools (F12)
3. Go to Console tab
4. Look for debug messages starting with 🔧

### 3. **Check Results**

**If you see "🎉 ALL ELEMENTS FOUND! Ready to test.":**
- Try adding an opening hour
- Check what happens in console

**If you see "❌ MISSING ELEMENTS:":**
- Note which elements are missing
- Check the template form field IDs

### 4. **Common Issues & Solutions**

#### Issue A: Missing Form Elements
```html
<!-- Make sure your form has these exact IDs: -->
<select id="id_day" name="day">...</select>
<select id="id_from_hour" name="from_hour">...</select>
<select id="id_to_hour" name="to_hour">...</select>
<input type="checkbox" id="id_is_closed" name="is_closed">
<input type="hidden" id="add_hour_url" value="{% url 'add_opening_hours' %}">
```

#### Issue B: URL Not Found (404)
- Check `vendor/urls.py` has: `path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours')`
- Ensure URL name matches in template: `{% url 'add_opening_hours' %}`

#### Issue C: Permission Denied (403)
- Make sure you're logged in as a vendor user
- Check that your user has a vendor profile

#### Issue D: Server Error (500)
- Check Django terminal for error details
- Look for import errors or database issues

### 5. **Manual Testing Commands**

Run these in browser console to test manually:

```javascript
// Test 1: Check all elements
console.log({
    day: document.getElementById('id_day'),
    from_hour: document.getElementById('id_from_hour'),
    to_hour: document.getElementById('id_to_hour'),
    is_closed: document.getElementById('id_is_closed'),
    url: document.getElementById('add_hour_url'),
    csrf: $('input[name=csrfmiddlewaretoken]').val()
});

// Test 2: Manual AJAX call
$.post('/vendor/opening-hours/add/', {
    day: '1',
    from_hour: '09:00 AM',
    to_hour: '05:00 PM',
    is_closed: 'False',
    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
}).done(function(data) {
    console.log('Success:', data);
}).fail(function(xhr) {
    console.log('Error:', xhr.responseText);
});
```

### 6. **After Fixing**
Remove the debug script from your template:
```html
<!-- Remove this line -->
<script src="{% static 'js/debug_opening_hours.js' %}"></script>
```

## Expected Console Output When Working:
```
🔧 DEBUG: Opening Hours Debug Script Loaded
🔍 CHECKING FORM ELEMENTS:
✅ Day element: FOUND
✅ From hour element: FOUND
✅ To hour element: FOUND
✅ Is closed element: FOUND
✅ CSRF token: FOUND
✅ URL element: FOUND
📍 Add hour URL: /vendor/opening-hours/add/
✅ Add hour button: FOUND
🎉 ALL ELEMENTS FOUND! Ready to test.
```

When you click "Add Hours":
```
🚀 ADD HOUR BUTTON CLICKED
📋 FORM VALUES: {day: "1", from_hour: "09:00 AM", ...}
📡 SENDING AJAX REQUEST...
⏳ REQUEST BEING SENT...
✅ SUCCESS RESPONSE: {status: "success", id: 123, ...}
🎉 Opening hour added successfully!
```
