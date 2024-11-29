from rest_framework import viewsets

from core.permissions import IsCustomer
from users.models import ShippingAddress
from users.serializers import ShippingAddressSerializer


# Create your views here.
class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)