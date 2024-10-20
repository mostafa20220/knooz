from rest_framework.routers import DefaultRouter
from .views import ProductReviewsViewSet
router = DefaultRouter()
router.register('', ProductReviewsViewSet, basename='reviews')

urlpatterns = router.urls

