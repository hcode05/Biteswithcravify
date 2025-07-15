from django.db import models
from accounts.models import User
from menu.models import FoodItem


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user


class Tax(models.Model):
    tax_type = models.CharField(max_length=50, unique=True, help_text="e.g., Sales Tax, VAT, Service Tax")
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Tax Percentage (%)', help_text="Enter percentage (e.g., 8.5 for 8.5%)")
    is_active = models.BooleanField(default=True, help_text="Check to enable this tax")

    class Meta:
        verbose_name = "Tax"
        verbose_name_plural = "Taxes"
        ordering = ['tax_type']

    def __str__(self):
        return f"{self.tax_type} ({self.tax_percentage}%)"
    
    def calculate_tax_amount(self, subtotal):
        """Calculate tax amount for given subtotal"""
        if self.is_active:
            return round((self.tax_percentage * subtotal) / 100, 2)
        return 0