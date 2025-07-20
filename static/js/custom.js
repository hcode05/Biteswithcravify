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
                    // Handle restaurant closed error specifically
                    if(response.restaurant_closed) {
                        swal({
                            title: "Restaurant Closed",
                            text: response.message,
                            icon: "warning",
                            buttons: {
                                confirm: {
                                    text: "OK",
                                    value: true,
                                    visible: true,
                                    className: "btn btn-warning",
                                    closeModal: true
                                }
                            }
                        });
                    } else {
                        swal(response.message, '', 'error');
                    }
                } else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.qty);

                    // Always apply cart amounts, not just on cart page
                    if(response.get_cart_amounts) {
                        applyCartAmounts(
                            response.get_cart_amounts['subtotal'],
                            response.get_cart_amounts['tax_dict'],
                            response.get_cart_amounts['grand_total']
                        );
                    }
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

                    // Always update cart amounts on all pages
                    if(response.get_cart_amounts) {
                        applyCartAmounts(
                            response.get_cart_amounts['subtotal'],
                            response.get_cart_amounts['tax_dict'],
                            response.get_cart_amounts['grand_total']
                        );
                    }

                    // Additional cart page specific updates
                    if(window.location.pathname == '/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
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

                    // Always update cart amounts on all pages
                    if(response.get_cart_amounts) {
                        applyCartAmounts(
                            response.get_cart_amounts['subtotal'],
                            response.get_cart_amounts['tax_dict'],
                            response.get_cart_amounts['grand_total']
                        );
                    }

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
        // Update cart amounts on cart page
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal);
            $('#total').html(grand_total);

            // Calculate total tax from tax_dict and update tax-total span
            let total_tax = 0;
            for(let key in tax_dict){
                for(let percent in tax_dict[key]){
                    total_tax += parseFloat(tax_dict[key][percent]);
                }
            }

            // Update the tax-total span
            $('#tax-total').html(total_tax.toFixed(2));
        }
        
        // Update any cart summary that might exist on other pages
        if($('#cart-subtotal').length) {
            $('#cart-subtotal').html(subtotal);
        }
        if($('#cart-tax').length) {
            let total_tax = 0;
            for(let key in tax_dict){
                for(let percent in tax_dict[key]){
                    total_tax += parseFloat(tax_dict[key][percent]);
                }
            }
            $('#cart-tax').html(total_tax.toFixed(2));
        }
        if($('#cart-total').length) {
            $('#cart-total').html(grand_total);
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

        console.log(day, from_hour, to_hour, is_closed, csrf_token)

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
                    if(response.status == 'success'){
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'/">Remove</a></td></tr>';
                        }else{
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.from_hour+' - '+response.to_hour+'</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'/">Remove</a></td></tr>';
                        }
                        
                        $(".opening_hours").append(html)
                        document.getElementById("opening_hours").reset();
                    }else{
                        swal(response.message, '', "error")
                    }
                }
            })
        }else{
            swal('Please fill all fields', '', 'info')
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
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()
                }
            }
        })
    })
    // document ready close 
    
});
