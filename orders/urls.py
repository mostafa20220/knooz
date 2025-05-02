from django.urls import path

from orders.views import OrderListAPIView, OrderDetailAPIView, ReturnOrderAPIView, CancelOrderAPIView, OrdersReportView, \
    ConfirmPaymentAPIView, ReorderAPIView, RepayOrderAPIView

urlpatterns =[
    path('', OrderListAPIView.as_view(), name='order-list'),
    path('report/', OrdersReportView.as_view(), name='order-report'),
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:pk>/cancel/', CancelOrderAPIView.as_view(), name='order-cancel'),
    path('<int:pk>/return/', ReturnOrderAPIView.as_view(), name='order-return'),
    path('confirm-payment/', ConfirmPaymentAPIView.as_view(), name='confirm-payment'),
    path('<int:pk>/reorder/', ReorderAPIView.as_view(), name='reorder'),
    path('<int:pk>/payment-link/', RepayOrderAPIView.as_view(), name='repay'),
]