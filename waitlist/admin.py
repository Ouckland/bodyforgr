# from django.contrib import admin
# from .models import WaitListUser
# # Register your models here.

# class WaitListUserAdmin(admin.ModelAdmin):
#     list_display = ('name', 'email', 'role', 'is_invited', 'source', 'created_at')
#     list_filter = ('role', 'is_invited', 'source', 'created_at')
#     search_fields = ('name', 'email', 'notes')
#     ordering = ('-created_at',)
    
# admin.site.register(WaitListUser, WaitListUserAdmin)

from django.contrib import admin
from .models import WaitListUser

@admin.register(WaitListUser)
class WaitListUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "role",
        "is_invited",
        "source",
        "created_at",
    )

    list_filter = ("role", "is_invited", "source")
    search_fields = ("email", "name")
    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("User Info", {
            "fields": ("name", "email", "role", "source"),
        }),
        ("Status", {
            "fields": ("is_invited", "notes"),
        }),
        ("Timestamps", {
            "fields": ("created_at",),
        }),
    )
