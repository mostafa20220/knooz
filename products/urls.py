
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, ProductVariantViewSet, VariantImageViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('variants', ProductVariantViewSet)
router.register('variant-images', VariantImageViewSet)

urlpatterns = router.urls

