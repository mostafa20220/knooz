from rest_framework.generics import CreateAPIView

from core.permissions import IsCustomer
from coupons.serializers import ApplyCouponSerializer

# apply coupon code
class ApplyCouponAPIView(CreateAPIView):
    serializer_class = ApplyCouponSerializer
    permission_classes = [IsCustomer]
