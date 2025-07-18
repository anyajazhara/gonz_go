from django import forms
from django.contrib import admin
from .models import FoodStall, MenuCategory, MenuItem, MenuOption, Order, OrderItem

# Register your models here.
admin.site.register(FoodStall)
admin.site.register(MenuCategory)
admin.site.register(MenuOption)

class MenuOptionInline(admin.TabularInline):
    model = MenuOption
    extra = 1

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        if not self.instance.pk:
            return cleaned_data  # skip check if item is not saved yet

        has_options = self.instance.options.exists()
        if not has_options and not price:
            raise forms.ValidationError("Price is required if no options are defined.")
        return cleaned_data

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm
    inlines = [MenuOptionInline]

    def get_fields(self, request, obj=None):
        fields = ['category', 'name', 'description']
        # Show price field only if no options exist yet (or if creating a new item)
        if obj is None or not obj.options.exists():
            fields.append('price')
        return fields
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'stall', 'user', 'placed_at', 'total', 'eta']
    inlines = [OrderItemInline]
    readonly_fields = ['placed_at']

admin.site.register(Order, OrderAdmin)