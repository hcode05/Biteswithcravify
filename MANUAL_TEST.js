// MANUAL TEST - Copy and paste this into your browser console
// Go to: http://localhost:8000/vendor/opening-hours/
// Open Developer Tools (F12) -> Console tab
// Paste this entire script and press Enter

console.log("🧪 MANUAL TEST STARTING...");

// Test 1: Check if jQuery is loaded
if (typeof $ === 'undefined') {
    console.error("❌ jQuery is not loaded!");
} else {
    console.log("✅ jQuery is loaded");
}

// Test 2: Check form elements
const elements = {
    day: document.getElementById('id_day'),
    from_hour: document.getElementById('id_from_hour'),
    to_hour: document.getElementById('id_to_hour'),
    is_closed: document.getElementById('id_is_closed'),
    csrf_token: document.querySelector('input[name="csrfmiddlewaretoken"]'),
    add_hour_url: document.getElementById('add_hour_url'),
    add_button: document.querySelector('.add_hour')
};

console.log("🔍 FORM ELEMENTS CHECK:");
Object.keys(elements).forEach(key => {
    const element = elements[key];
    console.log(`${element ? '✅' : '❌'} ${key}:`, element);
    
    if (key === 'add_hour_url' && element) {
        console.log(`📍 URL value: "${element.value}"`);
    }
    if (key === 'csrf_token' && element) {
        console.log(`🔑 CSRF token: "${element.value.substring(0, 10)}..."`);
    }
});

// Test 3: Check if table exists
const table = document.querySelector('.opening_hours');
console.log(`${table ? '✅' : '❌'} Opening hours table:`, table);

// Test 4: Manual button click test
if (elements.add_button) {
    console.log("🎯 MANUAL BUTTON CLICK TEST");
    console.log("Setting test values...");
    
    // Set test values
    if (elements.day) elements.day.value = '1'; // Monday
    if (elements.from_hour) elements.from_hour.value = '09:00 AM';
    if (elements.to_hour) elements.to_hour.value = '05:00 PM';
    if (elements.is_closed) elements.is_closed.checked = false;
    
    console.log("Test values set. Now run: $('.add_hour').click()");
    console.log("Or run this manual AJAX test:");
    console.log(`
$.ajax({
    type: 'POST',
    url: '${elements.add_hour_url ? elements.add_hour_url.value : '/vendor/opening-hours/add/'}',
    data: {
        'day': '1',
        'from_hour': '09:00 AM',
        'to_hour': '05:00 PM',
        'is_closed': 'False',
        'csrfmiddlewaretoken': '${elements.csrf_token ? elements.csrf_token.value : 'MISSING'}'
    },
    success: function(response) {
        console.log('✅ SUCCESS:', response);
    },
    error: function(xhr, status, error) {
        console.error('❌ ERROR:', xhr.responseText);
    }
});
    `);
} else {
    console.error("❌ Add button not found!");
}

console.log("🧪 MANUAL TEST COMPLETE");
console.log("👆 Follow the instructions above to test manually");
