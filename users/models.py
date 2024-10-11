from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

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

            print("Extra Fields: ", extra_fields)
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
        return self.email


class UserCreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    card_holder_name = models.CharField(max_length=50)
    expiration_date = models.TextField(max_length=5) # 03/26
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)