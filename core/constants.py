from decimal import Decimal

SHIPPING_FEE = Decimal('20')
SHIPPING_FEE_THRESHOLD = Decimal('200')

COD_FEE = Decimal('10')
ADDED_VALUE_TAX_RATE = Decimal('0.14')

CASH_ON_DELIVERY = 'cash on delivery'
CREDIT_CARD= 'credit card'

PAYMENT_METHOD_CHOICES = [
    (CREDIT_CARD, 'Credit Card'),
    (CASH_ON_DELIVERY, 'Cash on Delivery')
]

FREE = Decimal('0.00')