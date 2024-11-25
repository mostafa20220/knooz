from django.contrib import admin
from users.models import User, ShippingAddress
from .models import CreditCard
# Register your models here.
class CreditCardInline(admin.TabularInline):
    model = CreditCard
    extra = 0

class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress
    extra = 0

class UserAdmin(admin.ModelAdmin):
    inlines = [
        CreditCardInline,
        ShippingAddressInline,
    ]

# register the User model
admin.site.register(User, UserAdmin)

