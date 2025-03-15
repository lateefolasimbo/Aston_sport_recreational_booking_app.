from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Membership

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_staff')
    
    # Add 'role' to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    
    # Add 'role' to the add_fieldsets
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "membership_type", "status", "expiration_date", "auto_renew")
    list_filter = ("status", "membership_type", "auto_renew")
    search_fields = ("user__username", "membership_type")
