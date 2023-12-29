from django.contrib import admin
from .models import *


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'product')
    ordering = ('-created_at',)
    search_fields = ('pk', 'user', 'product')
admin.site.register(WishlistItem,WishlistAdmin)


admin.site.register(Cart)
admin.site.register(CartItem)

class PurchaseListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'total_amount')
admin.site.register(Purchase , PurchaseListAdmin)

admin.site.register(PurchaseItems)

class PurchaseAmountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'total_amount', 'tax', 'final_amount')
admin.site.register(PurchaseAmount, PurchaseAmountAdmin)
admin.site.register(PurchaseLog)

