let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }

    // get the address components and assign them to the fields
    // console.log(place);
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({'address': address}, function(results, status){
        // console.log('results=>', results)
        // console.log('status=>', status)
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            // console.log('lat=>', latitude);
            // console.log('long=>', longitude);
            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });

    // loop through the address components and assign other address data
    console.log(place.address_components);
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // get state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name);
            }
            // get city
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }else{
                $('#id_pin_code').val("");
            }
        }
    }

}

$(document).ready(function(){

    // ADD TO CART
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        let food_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response);
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    });
                } else if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    );
                }
            }
        });
    });

    // PLACE ITEM QTY ON LOAD
    $('.item_qty').each(function(){
        let the_id = $(this).attr('id');
        let qty = $(this).attr('data-qty');
        $('#' + the_id).html(qty);
    });

    // DECREASE CART
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();

        let food_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');
        let cart_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response);
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    });
                } else if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);

                    if(window.location.pathname == '/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();

                        applyCartAmounts(
                            response.cart_amount['subtotal'],
                            response.cart_amount['tax_dict'],
                            response.cart_amount['grand_total']
                        );
                    }
                }
            }
        });
    });

    // DELETE CART ITEM
    $('.delete_cart').on('click', function(e){
        e.preventDefault();

        let cart_id = $(this).attr('data-id');
        let url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response);
                if(response.status == 'Failed'){
                    swal(response.message, '', 'error');
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, "success");

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    );

                    removeCartItem(0, cart_id);
                    checkEmptyCart();
                }
            }
        });
    });

    // REMOVE ITEM IF QTY IS 0
    function removeCartItem(cartItemQty, cart_id){
        if(cartItemQty <= 0){
            document.getElementById("cart-item-" + cart_id).remove();
        }
    }

    // CHECK IF CART IS EMPTY
    function checkEmptyCart(){
        let cart_counter = document.getElementById('cart_counter').innerHTML;
        if(cart_counter == 0){
            document.getElementById("empty-cart").style.display = "block";
        }
    }

    // APPLY CART AMOUNTS (Subtotal, Tax, Grand Total)
    function applyCartAmounts(subtotal, tax_dict, grand_total){
        if(window.location.pathname == '/cart/'){
            console.log('applyCartAmounts called with:', {subtotal, tax_dict, grand_total});
            
            // Update subtotal and grand total
            $('#subtotal').html(subtotal);
            $('#total').html(grand_total);

            // Enhanced tax handling for dynamic tax system
            let total_tax = 0;
            
            // Clear existing dynamic tax items AND static template tax items to avoid duplicates
            $('.dynamic-tax-item').remove();
            $('.static-tax-item').remove();
            
            // Handle the new dynamic tax structure
            if (tax_dict && typeof tax_dict === 'object' && Object.keys(tax_dict).length > 0) {
                // Find the insertion point (after subtotal)
                let insertAfter = $('#subtotal').closest('li');
                
                for(let tax_type in tax_dict){
                    let tax_info = tax_dict[tax_type];
                    
                    if (typeof tax_info === 'object') {
                        // New dynamic tax structure
                        for(let rate in tax_info){
                            if (rate !== 'calculation_type' && rate !== 'description' && rate !== 'is_included') {
                                let tax_amount = parseFloat(tax_info[rate]);
                                if (!isNaN(tax_amount)) {
                                    total_tax += tax_amount;
                                    
                                    // Create or update tax breakdown item
                                    let tax_breakdown_html = `
                                        <li class="dynamic-tax-item" style="list-style-type: none; font-size: 0.9em; color: #666;">
                                            ${tax_type} (${rate}%)
                                            ${tax_info.is_included ? '<small style="color: #ffc107;">[Included]</small>' : ''}
                                            <span class="price float-right">
                                                <span class="currency">$</span>
                                                <span>${tax_amount.toFixed(2)}</span>
                                            </span>
                                        </li>
                                    `;
                                    insertAfter.after(tax_breakdown_html);
                                    insertAfter = insertAfter.next(); // Update insertion point
                                }
                            }
                        }
                    } else {
                        // Legacy tax structure support
                        let tax_amount = parseFloat(tax_info);
                        if (!isNaN(tax_amount)) {
                            total_tax += tax_amount;
                            
                            let tax_breakdown_html = `
                                <li class="dynamic-tax-item" style="list-style-type: none; font-size: 0.9em; color: #666;">
                                    ${tax_type}
                                    <span class="price float-right">
                                        <span class="currency">$</span>
                                        <span>${tax_amount.toFixed(2)}</span>
                                    </span>
                                </li>
                            `;
                            insertAfter.after(tax_breakdown_html);
                            insertAfter = insertAfter.next();
                        }
                    }
                }
            }

            // Update total tax display - make sure it updates
            if ($('#tax-total').length > 0) {
                $('#tax-total').html(total_tax.toFixed(2));
                console.log('Updated tax-total to:', total_tax.toFixed(2));
            } else {
                console.log('tax-total element not found');
            }
            
            // Force update of grand total to ensure consistency
            $('#total').html(grand_total);
            
            console.log('Final tax calculation:', {
                subtotal: subtotal,
                total_tax: total_tax.toFixed(2),
                grand_total: grand_total,
                tax_dict: tax_dict
            });
        }
    }
     // ADD OPENING HOUR
    $('.add_hour').on('click', function(e){
        e.preventDefault();
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value

        console.log(day, from_hour, to_hour, is_closed, csrf_token, url)

        // Day name mapping
        const dayNames = {
            '1': 'Monday',
            '2': 'Tuesday', 
            '3': 'Wednesday',
            '4': 'Thursday',
            '5': 'Friday',
            '6': 'Saturday',
            '7': 'Sunday'
        };

        if(is_closed){
            is_closed = 'True'
            condition = "day != ''"
        }else{
            is_closed = 'False'
            condition = "day != '' && from_hour != '' && to_hour != ''"
        }

        if(eval(condition)){
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function(response){
                    console.log('Response:', response);
                    if(response.status == 'success'){
                        // Use the day name from our mapping instead of response.day
                        var dayName = dayNames[day] || response.day;
                        
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id+'"><td>'+dayName+'</td><td>Closed</td><td><a href="#" class="remove_hour text-primary" data-url="/vendor/opening-hours/remove/'+response.id+'/" style="color: #007bff; text-decoration: none;">Remove</a></td></tr>';
                        }else{
                            html = '<tr id="hour-'+response.id+'"><td>'+dayName+'</td><td>'+response.from_hour+' - '+response.to_hour+'</td><td><a href="#" class="remove_hour text-primary" data-url="/vendor/opening-hours/remove/'+response.id+'/" style="color: #007bff; text-decoration: none;">Remove</a></td></tr>';
                        }
                        
                        $(".opening_hours tbody").append(html);
                        document.getElementById("opening_hours").reset();
                        
                        // Show success message
                        if(typeof swal !== 'undefined'){
                            swal('Success', 'Opening hour added successfully!', 'success');
                        } else {
                            alert('Opening hour added successfully!');
                        }
                    }else{
                        if(typeof swal !== 'undefined'){
                            swal(response.message, '', "error");
                        } else {
                            alert(response.message || 'Error adding opening hour');
                        }
                    }
                },
                error: function(xhr, status, error){
                    console.error('AJAX Error:', xhr.responseText);
                    if(typeof swal !== 'undefined'){
                        swal('Error', 'Failed to add opening hour. Please try again.', 'error');
                    } else {
                        alert('Failed to add opening hour. Please try again.');
                    }
                }
            })
        }else{
            if(typeof swal !== 'undefined'){
                swal('Please fill all fields', '', 'info');
            } else {
                alert('Please fill all fields');
            }
        }
    });

    // REMOVE OPENING HOUR
    $(document).on('click', '.remove_hour', function(e){
        e.preventDefault();
        url = $(this).attr('data-url');
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log('Remove response:', response);
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove();
                    if(typeof swal !== 'undefined'){
                        swal('Success', 'Opening hour removed successfully!', 'success');
                    } else {
                        alert('Opening hour removed successfully!');
                    }
                } else {
                    if(typeof swal !== 'undefined'){
                        swal('Error', response.message || 'Failed to remove opening hour', 'error');
                    } else {
                        alert(response.message || 'Failed to remove opening hour');
                    }
                }
            },
            error: function(xhr, status, error){
                console.error('AJAX Error:', xhr.responseText);
                if(typeof swal !== 'undefined'){
                    swal('Error', 'Failed to remove opening hour. Please try again.', 'error');
                } else {
                    alert('Failed to remove opening hour. Please try again.');
                }
            }
        })
    })
    
    // Initialize cart amounts on page load for cart page
    if(window.location.pathname == '/cart/'){
        console.log('Cart page loaded - initializing amounts');
        
        // Remove static tax items immediately to prevent duplicates
        $('.static-tax-item').remove();
        
        console.log('Static tax items removed on page load');
    }
    
    // document ready close 
    
});
