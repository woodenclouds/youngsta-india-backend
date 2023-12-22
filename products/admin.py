from django.contrib import admin
from .models import *


# admin.site.register(ProductItem)
admin.site.register(ProductTag)

class ProductImageInline(admin.TabularInline):  # or StackedInline
    model = ProductImages

@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

# admin.site.register(SubCategory)



class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'position')
    ordering = ('position',)
    search_fields = ('pk', 'name',)
admin.site.register(SubCategory,SubCategoryAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display=('pk', 'name', 'position' )
    ordering = ('position',)
admin.site.register(Category,  CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display=('pk', 'name', )
admin.site.register(Brand, BrandAdmin)

class AtributeAdmin(admin.ModelAdmin):
    list_display=('pk', 'title', )
admin.site.register(Attribute, AtributeAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display=('pk', 'name', )
    search_fields = ('pk', 'name',)
    def get_brand_name(self, obj):
        return obj.brand.name if obj.brand else ''
    get_brand_name.short_description = 'Brand'

admin.site.register(Product, ProductAdmin)