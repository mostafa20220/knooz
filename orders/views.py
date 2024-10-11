from django.shortcuts import render
from rest_framework import viewsets

from carts.permissions import IsCustomerOrReadOnly
from orders.models import Order


# Create your views here.
class OrderSerializer:
  pass


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)