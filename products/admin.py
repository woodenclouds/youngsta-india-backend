from django.contrib import admin
from .models import *


admin.site.register(Product)
admin.site.register(Category)
# admin.site.register(ProductItem)
admin.site.register(ProductTag)
admin.site.register(Company)
class ProductImageInline(admin.TabularInline):  # or StackedInline
    model = ProductImages

@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]