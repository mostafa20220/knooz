from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

from core.permissions import IsCustomer
from orders.models import Order
from orders.serializers import OrderSerializer



class OrderListAPIView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user).prefetch_related('items')


class OrderDetailAPIView(RetrieveUpdateAPIView):
    # the update req can only cancel the order if it is not shipped yet
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related('items')