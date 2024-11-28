from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from core.models import BaseTimeStamp

CUSTOMER = 'CUSTOMER'
SELLER = 'SELLER'
ADMIN = 'ADMIN'
STAFF = 'STAFF'
USER_TYPE_CHOICES = [
    (CUSTOMER, 'Customer'),
    (SELLER, 'Seller'),
    (ADMIN, 'Admin'),
    (STAFF, 'Staff'),
]

class UserManger(BaseUserManager):
    def create_user(self, email, password=None ,**extra_fields):

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', CUSTOMER)

        if not email:
            raise ValueError('Users must have an email address')

        try:
            user = self.model(
                email=self.normalize_email(email),
                **extra_fields)

            user.set_password(password)
            user.save(using=self._db)
            return user
        except Exception as e:
            raise ValueError('Error while creating user:', e)

    def create_superuser(self, email, password=None, **extra_fields):
        try:
            extra_fields.setdefault('is_active', True)
            extra_fields.setdefault('user_type', STAFF)

            
            user = self.create_user(
                email=email,
                **extra_fields
            )
            user.set_password(password)
            user.is_admin = True
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.save(using=self._db)
            return user
        except Exception as e:
            raise ValueError('Error while creating superuser:', e)


class User(AbstractUser):

    objects = UserManger()

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, blank=True ,choices=USER_TYPE_CHOICES, default=CUSTOMER)
    phone = PhoneNumberField(_("Phone Number"), blank=True, null=True)
    image = models.ImageField(upload_to='profile/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    username = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type', 'is_active', 'image']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        result = []
        for name in [self.first_name, self.last_name]:
            if name:
                result.append(name)
        return ' '.join(result)


class CreditCard(BaseTimeStamp):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='credit_cards')
    card_number = models.CharField(max_length=16)
    card_holder_name = models.CharField(max_length=50)
    expiration_date = models.TextField(max_length=5) # 03/26
    is_default = models.BooleanField(default=False)


class ShippingAddress(BaseTimeStamp):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='shipping_addresses')

    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50,null=True,blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    street = models.CharField(max_length=255)
    building_number = models.PositiveIntegerField()
    floor_number = models.PositiveIntegerField(null=True,blank=True)
    apartment_number = models.PositiveIntegerField(null=True,blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'country', 'city', 'postal_code', 'street', 'building_number','floor_number','apartment_number'], name='unique_address')
        ]

    def save( self,*args, **kwargs):
        if self.is_default:
            try:
                ShippingAddress.objects.filter(user=self.user).update(is_default=False)
            except Exception as e:
                raise ValueError('Error while updating default shipping address:', e)
        super(ShippingAddress, self).save(*args,**kwargs)

    def __str__(self):
        fields = ['apartment_number', 'floor_number', 'building_number', 'street', 'postal_code', 'city', 'state', 'country', 'description']
        # create the shipping address snapshot where each field : field value is separated by a comma
        address_list = []
        for field in fields:
            value = getattr(self, field)
            if value:
                address_list.append(f"{field}: {value}")
        shipping_address_snapshot = ', '.join(address_list)
        return shipping_address_snapshot
