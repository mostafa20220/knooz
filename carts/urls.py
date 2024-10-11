
from rest_framework.routers import DefaultRouter

from carts.views import CartViewSet

router = DefaultRouter()
router.register('', CartViewSet)

urlpatterns = router.urls

