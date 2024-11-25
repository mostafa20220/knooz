from django.contrib import admin
from .models import Cart
# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer','product_variant','quantity']
    readonly_fields = ['customer']

admin.site.register(Cart, CartAdmin)