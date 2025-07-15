// Debug version of the add_hour functionality
// Instructions:
// 1. Include this script in your opening_hours.html template
// 2. Open browser Developer Tools (F12) 
// 3. Go to Console tab
// 4. Try adding opening hours and check the logs

$(document).ready(function(){
    console.log("🔧 DEBUG: Opening Hours Debug Script Loaded");
    
    // Wait a moment for DOM to be fully ready
    setTimeout(function() {
        console.log("🔍 CHECKING FORM ELEMENTS:");
        
        // Check if elements exist
        const dayElement = document.getElementById('id_day');
        const fromHourElement = document.getElementById('id_from_hour');
        const toHourElement = document.getElementById('id_to_hour');
        const isClosedElement = document.getElementById('id_is_closed');
        const urlElement = document.getElementById('add_hour_url');
        const csrfToken = $('input[name=csrfmiddlewaretoken]').val();
        
        console.log("✅ Day element:", dayElement ? "FOUND" : "❌ MISSING", dayElement);
        console.log("✅ From hour element:", fromHourElement ? "FOUND" : "❌ MISSING", fromHourElement);
        console.log("✅ To hour element:", toHourElement ? "FOUND" : "❌ MISSING", toHourElement);
        console.log("✅ Is closed element:", isClosedElement ? "FOUND" : "❌ MISSING", isClosedElement);
        console.log("✅ CSRF token:", csrfToken ? "FOUND" : "❌ MISSING", csrfToken);
        console.log("✅ URL element:", urlElement ? "FOUND" : "❌ MISSING", urlElement);
        
        if (urlElement) {
            console.log("📍 Add hour URL:", urlElement.value);
        }
        
        // Check if button exists
        const addButton = $('.add_hour');
        console.log("✅ Add hour button:", addButton.length ? "FOUND" : "❌ MISSING", addButton);
        
        // List all missing elements
        const missing = [];
        if (!dayElement) missing.push("id_day");
        if (!fromHourElement) missing.push("id_from_hour");
        if (!toHourElement) missing.push("id_to_hour");
        if (!isClosedElement) missing.push("id_is_closed");
        if (!urlElement) missing.push("add_hour_url");
        if (!csrfToken) missing.push("csrf token");
        if (!addButton.length) missing.push(".add_hour button");
        
        if (missing.length > 0) {
            console.error("❌ MISSING ELEMENTS:", missing);
            console.log("💡 TIP: Check your template form field IDs and button class");
        } else {
            console.log("🎉 ALL ELEMENTS FOUND! Ready to test.");
        }
    }, 500);
    
    // Override the add_hour click handler for debugging
    $(document).off('click', '.add_hour'); // Remove any existing handlers
    $('.add_hour').on('click', function(e){
        console.log("🚀 ADD HOUR BUTTON CLICKED");
        e.preventDefault();
        
        var day = document.getElementById('id_day')?.value;
        var from_hour = document.getElementById('id_from_hour')?.value;
        var to_hour = document.getElementById('id_to_hour')?.value;
        var is_closed = document.getElementById('id_is_closed')?.checked;
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var url = document.getElementById('add_hour_url')?.value;

        console.log("📋 FORM VALUES:", {
            day: day,
            from_hour: from_hour,
            to_hour: to_hour,
            is_closed: is_closed,
            csrf_token: csrf_token ? "Present" : "Missing",
            url: url
        });
        
        // Check critical requirements
        if (!url) {
            console.error("❌ URL is missing!");
            alert("❌ ERROR: URL is missing! Check if 'add_hour_url' element exists in your template.");
            return;
        }
        
        if (!csrf_token) {
            console.error("❌ CSRF token is missing!");
            alert("❌ ERROR: CSRF token is missing! Check if {% csrf_token %} is in your form.");
            return;
        }
        
        // Validate fields based on is_closed status
        if (is_closed) {
            if (!day) {
                console.warn("⚠️ Day is required even when closed");
                alert("⚠️ Please select a day");
                return;
            }
            console.log("ℹ️ Restaurant is closed on this day");
        } else {
            if (!day || !from_hour || !to_hour) {
                console.warn("⚠️ All fields required when not closed");
                alert("⚠️ Please fill all fields (day, from hour, to hour)");
                return;
            }
            console.log("ℹ️ Restaurant is open with hours");
        }
        
        console.log("📡 SENDING AJAX REQUEST...");
        console.log("🎯 URL:", url);
        console.log("📦 Data:", {
            'day': day,
            'from_hour': from_hour,
            'to_hour': to_hour,
            'is_closed': is_closed ? 'True' : 'False',
            'csrfmiddlewaretoken': 'Present'
        });
        
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'day': day,
                'from_hour': from_hour,
                'to_hour': to_hour,
                'is_closed': is_closed ? 'True' : 'False',
                'csrfmiddlewaretoken': csrf_token,
            },
            beforeSend: function() {
                console.log("⏳ REQUEST BEING SENT...");
            },
            success: function(response){
                console.log('✅ SUCCESS RESPONSE:', response);
                
                if (response.status === 'success') {
                    console.log('🎉 Opening hour added successfully!');
                    
                    // Create the HTML row
                    let html;
                    if (response.is_closed === 'Closed') {
                        html = `<tr id="hour-${response.id}">
                                    <td><b>${response.day}</b></td>
                                    <td>Closed</td>
                                    <td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td>
                                </tr>`;
                    } else {
                        html = `<tr id="hour-${response.id}">
                                    <td><b>${response.day}</b></td>
                                    <td>${response.from_hour} - ${response.to_hour}</td>
                                    <td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td>
                                </tr>`;
                    }
                    
                    console.log('📝 Adding HTML:', html);
                    $(".opening_hours tbody").append(html);
                    
                    // Reset the form
                    document.getElementById("opening_hours").reset();
                    
                    alert('✅ SUCCESS: Opening hour added successfully!');
                } else {
                    console.error('❌ Server returned failure:', response.message);
                    alert('❌ ERROR: ' + (response.message || 'Unknown error'));
                }
            },
            error: function(xhr, status, error){
                console.error('❌ AJAX ERROR:', {
                    status: status,
                    error: error,
                    responseText: xhr.responseText,
                    statusCode: xhr.status
                });
                
                let errorMessage = 'Network error occurred';
                if (xhr.status === 404) {
                    errorMessage = 'URL not found (404). Check your URL configuration.';
                } else if (xhr.status === 403) {
                    errorMessage = 'Permission denied (403). Check authentication.';
                } else if (xhr.status === 500) {
                    errorMessage = 'Server error (500). Check Django logs.';
                } else if (xhr.responseText) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMessage = response.message || xhr.responseText;
                    } catch (e) {
                        errorMessage = xhr.responseText;
                    }
                }
                
                alert('❌ ERROR: ' + errorMessage);
            }
        });
    });
});
