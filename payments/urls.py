from django.urls import path
from payments.views import InitiatePaymentView


urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
]