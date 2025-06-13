from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Discount

class DiscountInline(admin.TabularInline):
    model = Discount
    extra = 1 # Number of empty forms to display
    fields = ('name', 'discount_percentage', 'start_date', 'end_date', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price', 'display_price', 'on_sale', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    autocomplete_fields = ['category']
    readonly_fields = ('display_price', 'on_sale', 'image_preview') # Calculated fields
    inlines = [DiscountInline]
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'description', 'price', 'image', 'image_preview')
        }),
        ('Status', {
            'fields': ('display_price', 'on_sale')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            try:
                # First try to get the thumbnail URL
                if hasattr(obj, 'image_thumbnail') and obj.image_thumbnail:
                    image_url = obj.image_thumbnail.url
                else:
                    # Fallback to original image
                    image_url = obj.image.url
                
                return format_html(
                    '<img src="{}" style="max-height: 50px; object-fit: contain;" alt="{}"/>',
                    image_url,
                    obj.name
                )
            except Exception as e:
                return format_html(
                    '<span style="color: red;">Error: {}</span>',
                    str(e)
                )
        return "No image"
    image_preview.short_description = 'Image Preview'

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'discount_percentage', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date', 'product__category')
    search_fields = ('name', 'product__name')
    autocomplete_fields = ['product']
    ordering = ['-start_date']
    fieldsets = (
        (None, {
            'fields': ('product', 'name', 'discount_percentage')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )
