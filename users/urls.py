from rest_framework.routers import DefaultRouter

from users.views import ShippingAddressViewSet

router = DefaultRouter()

router.register('', ShippingAddressViewSet, basename='shipping-address')

urlpatterns = router.urls
