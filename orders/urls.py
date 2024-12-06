from django.urls import path

from orders.views import OrderListAPIView, OrderDetailAPIView, ReturnOrderAPIView, CancelOrderAPIView, OrdersReportView

urlpatterns =[
    path('', OrderListAPIView.as_view(), name='order-list'),
    path('report/', OrdersReportView.as_view(), name='order-report'),
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', CancelOrderAPIView.as_view(), name='order-cancel'),
    path('<int:pk>/return/', ReturnOrderAPIView.as_view(), name='order-return'),

]