from django.contrib import admin
from django.core.paginator import Paginator
from django.utils.functional import cached_property

from .models import Order, OrderItem
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


class DumbPaginator(Paginator):
    """
    Paginator that does not count the rows in the table.
    """
    @cached_property
    def count(self):
        return 9999999999


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'quantity', 'item_price']
    list_select_related = ['order','variant','seller']
    raw_id_fields=['order','variant','seller']
    show_full_result_count = False

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)