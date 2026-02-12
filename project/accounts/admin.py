from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User


# Register your models here.

@admin.register(User)
class LibraryAdmin(UserAdmin):
    list_display = ("username", 'email', "is_admin", 'is_staff', 'date_joined')
    list_filter = ('is_admin', "is_staff")
    fieldsets = UserAdmin.fieldsets + (
    ("추가정보", {"fields": ("is_admin", )}),
    )
