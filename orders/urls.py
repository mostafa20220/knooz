from django.urls import path

from orders.views import OrderListAPIView, OrderDetailAPIView

urlpatterns =[
    path('', OrderListAPIView.as_view(), name='order-list'),
    path('<pk>/', OrderDetailAPIView.as_view(), name='order-detail'),

]