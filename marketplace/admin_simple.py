from django.contrib import admin
from .models import Cart, Tax


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'fooditem', 'quantity', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'fooditem__food_title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active', 'formatted_rate')
    list_filter = ('is_active',)
    search_fields = ('tax_type',)
    list_editable = ('tax_percentage', 'is_active')
    ordering = ('tax_type',)
    
    fieldsets = (
        ('Tax Information', {
            'fields': ('tax_type', 'tax_percentage', 'is_active'),
            'description': 'Configure different types of taxes for your marketplace'
        }),
    )
    
    def formatted_rate(self, obj):
        """Display tax percentage in a formatted way"""
        return f"{obj.tax_percentage}%"
    formatted_rate.short_description = 'Tax Rate'
    formatted_rate.admin_order_field = 'tax_percentage'
    
    def save_model(self, request, obj, form, change):
        """Custom save logic if needed"""
        super().save_model(request, obj, form, change)
        if change:
            # Log the change
            print(f"Tax {obj.tax_type} updated to {obj.tax_percentage}%")
    
    class Meta:
        verbose_name = "Tax"
        verbose_name_plural = "Taxes"


# Register the models
admin.site.register(Cart, CartAdmin)
