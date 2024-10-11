from django.contrib import admin
from users.models import User
from .models import UserCreditCard
# Register your models here.

# register the User model
admin.site.register([User, UserCreditCard])

