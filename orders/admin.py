from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)