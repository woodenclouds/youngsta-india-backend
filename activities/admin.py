from django.contrib import admin
from .models import *


class WishlistAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "product")
    ordering = ("-created_at",)
    search_fields = ("pk", "user", "product")


admin.site.register(WishlistItem, WishlistAdmin)


admin.site.register(Cart)
admin.site.register(CartItem)


class PurchaseListAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "address", "created_at", "total_amount")
    ordering = ["created_at"]


admin.site.register(Purchase, PurchaseListAdmin)

admin.site.register(PurchaseItems)


class PurchaseAmountAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "total_amount",
        "tax",
        "final_amount",
        "payment_method",
    )
    ordering = ["-created_at"]


admin.site.register(PurchaseAmount, PurchaseAmountAdmin)


class AdminPurchaseLogs(admin.ModelAdmin):
    list_display = ("pk", "user_name", "log_status")

    def user_name(self, obj):
        return (
            obj.Purchases.user.username
            if obj.Purchases and obj.Purchases.user
            else "N/A"
        )

    user_name.short_description = "User Name"


admin.site.register(PurchaseLog, AdminPurchaseLogs)

# admin.site.register(PurchaseLogs)


@admin.register(PurchaseStatus)
class PurchaseStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "order_id")
    ordering = ("order_id",)


admin.site.register(Referral)
