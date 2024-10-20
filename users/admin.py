from django.contrib import admin
from users.models import User, ShippingAddress
from .models import CreditCard
# Register your models here.

# register the User model
admin.site.register([User, CreditCard,ShippingAddress])

