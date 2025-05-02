import json
from datetime import timedelta
from django.utils import timezone
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from core.constants import CREDIT_CARD
from orders.services import empty_customer_cart, create_payment_intention, restock_order, cancel_order, validate_hmac
from carts.models import Cart
from utils.emails import send_email_async
from utils.loggers import log_error, log_warning, log_info

from django.db import transaction
from django.db.models import F, Sum, Max, Min, Avg, Value
from django.db.models.functions import TruncWeek, Concat
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.permissions import IsCustomer
from orders.models import Order, CANCELLED, PENDING, PLACED, DELIVERED, RETURNED, OrderItem, PAYMENT_FAILED, REFUNDED, \
    REFUND_FAILED
from orders.serializers import OrderSerializer


class OrderListAPIView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    OrderingFilter = '-created_at'

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related('items')


class OrderDetailAPIView(RetrieveAPIView):
    # the update req can only cancel the order if it is not shipped yet
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related('items')



class CancelOrderAPIView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            customer = request.user
            order = Order.objects.filter(pk=pk,customer=customer).first()

            if not order:
                return Response({'error': 'Order not found'}, status=HTTP_404_NOT_FOUND)
            if order.order_status not in [PENDING, PLACED, PAYMENT_FAILED]:
                return Response({'error': f'Order is {order.order_status} already'}, status=HTTP_400_BAD_REQUEST)

            is_cancelled = cancel_order(order)
            if not is_cancelled:
                return Response({'error': 'Error while cancelling order, try again later or contact support if the problem persist'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message': 'Order cancelled successfully'}, status=HTTP_200_OK)

        except Exception as e:
            log_error(f"Error while cancelling order in CancelOrderAPIView: {e}")
            return Response({'error': 'Error while cancelling order, try again later or contact support if the problem persist'}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class ReturnOrderAPIView(CreateAPIView):
    permission_classes = [IsCustomer]

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        customer = request.user
        order = Order.objects.filter(pk=pk,customer=customer).first()
        if not order:
            return Response({'error': 'Order not found'}, status=404)
        if order.order_status == DELIVERED:
            with transaction.atomic():
                order.order_status = RETURNED
                order.save()
        else:
            return Response({'error': f'Order is {order.order_status} already'}, status=400)
        return Response(OrderSerializer(order).data)


class OrdersReportView(APIView):
    def get(self, request):
        report = (OrderItem.objects
                  .annotate(week=TruncWeek('order__created_at'))
                  .values('week','seller')
                  .annotate(total_selling=Sum(F('item_price') * F('quantity')),
                            max_selling=Max(F('item_price')  * F('quantity')),
                            min_selling=Min(F('item_price')  * F('quantity')),
                            avg_selling=Avg(F('item_price')  * F('quantity')),
                            seller_name=Concat(F('seller__first_name'),
                            Value(" "), F('seller__last_name'))
                            )
                  .values('week', "seller_id", "seller_name" , 'min_selling','max_selling','total_selling')
                  .order_by('-week')
                  [:10]
                  )
        return Response(report)

class ReorderAPIView(CreateAPIView):
    permission_classes = [IsCustomer]

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        customer = request.user
        order = Order.objects.filter(pk=pk,customer=customer).first()
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        empty_customer_cart(customer)
        new_cart_items = [Cart(customer=customer, product_variant=item.variant, quantity=item.quantity) for item in order.items.all()]
        Cart.objects.bulk_create(new_cart_items)

        return Response({'message': 'Order items added to the cart successfully'}, status=status.HTTP_201_CREATED)

class RepayOrderAPIView(ListAPIView):
    permission_classes = [IsCustomer]

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        customer = request.user
        try:
            order = Order.objects.filter(pk=pk,customer=customer).first()
            if not order:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            if order.payment_method != CREDIT_CARD:
                return Response({'error': 'Only credit card payment method is supported for repayment'}, status=status.HTTP_400_BAD_REQUEST)
            if order.order_status not in [PAYMENT_FAILED, PENDING]:
                return Response({'error': f'Order Status is {order.order_status} already!, can\'t repay this order.'}, status=status.HTTP_400_BAD_REQUEST)
            if order.created_at < timezone.now() - timedelta(hours=1):
                return Response({'error': 'The repayment time limit has been exceeded'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                response = create_payment_intention(order, order.shipping_address)
                return Response(response)
            except Exception as e:
                log_error(f"Error while creating payment intention: {e}")
                return Response({'error': 'Error while creating payment intention, try again later'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            log_error(f"Error while repaying order: {e}")
            return Response({'error': 'Error while repaying order, try again later or contact support if the problem persist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ConfirmPaymentAPIView(CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body).get("obj")
            received_hmac = request.query_params.get('hmac')

            if not validate_hmac(payload, received_hmac):
                return Response({"error": "Invalid HMAC signature"}, status=status.HTTP_400_BAD_REQUEST)

            order_id = payload.get('payment_key_claims').get('extra').get('order_id')
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(pk=order_id).only('order_status', 'customer')
                if not order:
                    return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
                if  payload.get('success') and (payload.get('is_voided') or payload.get('is_refunded')):
                    log_info(f"order refunded successfully, payload: {payload}")
                    order.update(order_status=REFUNDED)
                    send_email_async("Order refunded", f"Your order {order_id} has been refunded", [order.first().customer.email])
                    return Response(status=status.HTTP_200_OK)
                if  not payload.get('success') and (payload.get('is_voided') or payload.get('is_refunded')):
                    log_info(f"order refunded failed, payload: {payload}")
                    order.update(order_status=REFUND_FAILED)
                    send_email_async("Refunded failed", f"Your Refund for order {order_id} has failed", [order.first().customer.email])
                    return Response(status=status.HTTP_200_OK)

                if not payload.get('success') :
                    log_info(f"Payment failed, payload: {payload}")
                    order.update(order_status=PAYMENT_FAILED)
                    send_email_async("Payment Failed", f"Your payment for order {order_id} has failed", [order.first().customer.email])
                    return Response(status=status.HTTP_200_OK)

                transaction_id = payload.get('id')
                order.update(order_status=PLACED,paymob_transaction_id=transaction_id)
                send_email_async("Your order has been placed", f"Your order has been placed successfully with order id: {order_id}", [order.first().customer.email])
                return Response(status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)



