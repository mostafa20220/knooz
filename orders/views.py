from django.db import transaction
from django.db.models import F, Sum, Max, Min, Avg, Value
from django.db.models.functions import TruncWeek, Concat
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from core.permissions import IsCustomer
from orders.models import Order, CANCELLED, PENDING, PLACED, DELIVERED, RETURNED, OrderItem
from orders.serializers import OrderSerializer
from products.models import ProductVariant

class OrderListAPIView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_queryset(self):
        self.queryset.filter(customer=self.request.user).prefetch_related('items')
        return self.queryset


class OrderDetailAPIView(RetrieveAPIView):
    # the update req can only cancel the order if it is not shipped yet
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user).prefetch_related('items')


class CancelOrderAPIView(CreateAPIView):
    permission_classes = [IsCustomer]

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        customer = request.user
        order = Order.objects.filter(pk=pk,customer=customer).first()
        print("found order to cancel: ", order)
        if not order:
            return Response({'error': 'Order not found'}, status=404)
        if order.order_status in [PENDING, PLACED]:
            with transaction.atomic():

                # update the stock
                variants_to_update = []
                for item in order.items.all():
                    print("item: ", item)
                    print("old stock: ", item.variant.stock)
                    item.variant.stock += item.quantity
                    print("new stock: ", item.variant.stock)
                    variants_to_update.append(item.variant)

                ProductVariant.objects.bulk_update(variants_to_update, ['stock', 'updated_at'], 500)

                # update the order status
                order.order_status = CANCELLED
                order.save()

        else :
            return Response({'error': f'Order is {order.order_status} already'}, status=400)
        return Response(OrderSerializer(order).data)


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
        print("report query: ",str(report.query))
        return Response(report)
