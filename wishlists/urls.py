from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import ShippingAddressViewSet
from wishlists.views import WishlistViewSet

router = DefaultRouter()

router.register('', WishlistViewSet, basename='wishlist')


urlpatterns = router.urls
