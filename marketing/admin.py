from django.contrib import admin
from .models import *


class AdsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'position')
    ordering = ('-created_at',)
    search_fields = ('pk', 'title',)
admin.site.register(Ads,AdsAdmin)



class AdItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'position')
    ordering = ('-created_at',)
    search_fields = ('pk', 'title',)
admin.site.register(AdsItem,AdItemAdmin)