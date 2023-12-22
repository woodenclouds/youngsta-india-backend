from django.contrib import admin
from .models import *


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'product')
    ordering = ('-created_at',)
    search_fields = ('pk', 'user', 'product')
admin.site.register(WishlistItem,WishlistAdmin)
