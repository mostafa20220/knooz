from django.contrib import admin
from users.models import User, ShippingAddress
# Register your models here.

class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress
    extra = 0

class UserAdmin(admin.ModelAdmin):
    inlines = [
        ShippingAddressInline,
    ]

# register the User model
admin.site.register(User, UserAdmin)

