from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(AdminProfile)
admin.site.register(UserProfile)
admin.site.register(Address)

class StaffAdmin(admin.ModelAdmin):
    list_display = ('pk', 'fullname', 'email', 'type')
admin.site.register(Staff, StaffAdmin)
