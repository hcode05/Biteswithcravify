from django.contrib import admin
from .models import Payment, Order, OrderedFood

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount')
    extra = 0

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'transaction_id', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    list_filter = ['status', 'is_ordered', 'payment_method', 'created_at']
    search_fields = ['order_number', 'name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderedFoodInline]

class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'fooditem', 'quantity', 'price', 'amount']
    list_filter = ['order__status', 'created_at']

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood, OrderedFoodAdmin)