import random

from celery.concurrency import custom
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer
from core.tasks import send_otp_task
from users.models import ShippingAddress
from users.serializers import ShippingAddressSerializer
from utils.sms import send_sms_async, send_otp_async


# Create your views here.
class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TestSMSView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request, *args, **kwargs):
        customer = request.user
        phone = str(customer.phone)
        send_sms_async('Hello from knooz!', [phone])
        # random otp generation
        otp = random.randint(100_000, 999_999)
        send_otp_async(otp, phone)
        return Response({'detail': 'Request To SMS sent successfully!'})