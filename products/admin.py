from django.contrib import admin
from .models import *


# admin.site.register(ProductItem)
admin.site.register(ProductTag)
admin.site.register(AttributeType)
admin.site.register(AttributeDescription)

# class ProductImageInline(admin.TabularInline):  # or StackedInline
#     model = ProductImages

# @admin.register(ProductVarient)
# class ProductItemAdmin(admin.ModelAdmin):
#     inlines = [ProductImageInline]

# admin.site.register(SubCategory)

# class CategoryAdmin(admin.ModelAdmin):
#     list_display=('pk', 'name', )
# admin.site.register(Category, CategoryAdmin)
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
    list_display=('pk','attribute' ,'attribute_value')
admin.site.register(Attribute, AtributeAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display=('pk', 'name', )
    search_fields = ('pk', 'name',)

admin.site.register(Product, ProductAdmin)

class ProductGalleryAdmin(admin.ModelAdmin):
    list_display=('pk', 'image_name', )
    search_fields = ('pk', 'image_name',)

admin.site.register(ProductGallery, ProductGalleryAdmin)

admin.site.register(ProductAttribute)

class ProductImagesAdmin(admin.ModelAdmin):
    list_display=('pk', 'image' )
    search_fields = ('pk', 'image' )

admin.site.register(ProductImages, ProductImagesAdmin)

# class ProductImageAdmin(admin.ModelAdmin):
#     list_display=("pk","product", "image", "thumbnail")
# admin.site.register(ProductImages, ProductImageAdmin)