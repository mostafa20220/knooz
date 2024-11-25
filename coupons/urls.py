from django.urls import path

from coupons.views import ApplyCouponAPIView

urlpatterns = [
    path('', ApplyCouponAPIView.as_view(), name='apply-coupon'),
]