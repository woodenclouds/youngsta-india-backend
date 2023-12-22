from django.contrib import admin
from .models import *


admin.site.register(Product)

# admin.site.register(ProductItem)
admin.site.register(ProductTag)

class ProductImageInline(admin.TabularInline):  # or StackedInline
    model = ProductImages

@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

# admin.site.register(SubCategory)

class CategoryAdmin(admin.ModelAdmin):
    list_display=('pk', 'name', )
admin.site.register(Category, CategoryAdmin)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description')
    ordering = ('-created_at',)
    search_fields = ('pk', 'name',)
admin.site.register(SubCategory,SubCategoryAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display=('pk', 'name','orders' )
    ordering = ('orders',)
admin.site.register(Category,  CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display=('pk', 'name', )
admin.site.register(Brand, BrandAdmin)



class AtributeAdmin(admin.ModelAdmin):
    list_display=('pk', 'title', )
admin.site.register(Attribute, AtributeAdmin)