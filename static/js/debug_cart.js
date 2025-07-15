/* Add this JavaScript to your cart page to debug tax calculations */

// Debug function to test cart amount updates
function debugCartAmounts() {
    console.log("=== Debugging Cart Amounts ===");
    
    // Check if required elements exist
    const elements = {
        subtotal: $('#subtotal'),
        taxTotal: $('#tax-total'),
        grandTotal: $('#total')
    };
    
    console.log("Elements found:", {
        subtotal: elements.subtotal.length > 0,
        taxTotal: elements.taxTotal.length > 0,
        grandTotal: elements.grandTotal.length > 0
    });
    
    // Get current values
    console.log("Current values:", {
        subtotal: elements.subtotal.text(),
        taxTotal: elements.taxTotal.text(),
        grandTotal: elements.grandTotal.text()
    });
    
    // Test applyCartAmounts function with sample data
    const testData = {
        subtotal: 100.00,
        tax_dict: {
            'SGST': {
                '7.0': 7.00
            },
            'CGST': {
                '5.0': 5.00
            }
        },
        grand_total: 112.00
    };
    
    console.log("Testing with sample data:", testData);
    applyCartAmounts(testData.subtotal, testData.tax_dict, testData.grand_total);
}

// Run debug function when page loads
$(document).ready(function() {
    if(window.location.pathname == '/cart/') {
        setTimeout(debugCartAmounts, 1000); // Run after 1 second to ensure page is loaded
    }
});

// Make function available globally for manual testing
window.debugCartAmounts = debugCartAmounts;
