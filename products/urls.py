from django.urls import path
from .views import ProductListView, ProductDetailView, SizeListView, ColorListView, CategoryListView, BrandListView

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='products-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='products-detail'),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('brands/', BrandListView.as_view(), name='brands-list'),
    path('colors/', ColorListView.as_view(), name='colors-list'),
    path('sizes/', SizeListView.as_view(), name='sizes-list'),

]