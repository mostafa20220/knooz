from django.urls import path

from .views import ProductListView, ProductDetailView, VariantDetailView, ImageDetailView

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('variants/<pk>/', VariantDetailView.as_view(), name='variant-detail'),
    path('images/<pk>/', ImageDetailView.as_view(), name='image-detail'),
    ]

