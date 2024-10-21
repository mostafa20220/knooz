from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import serve
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
  path('auth/', include('djoser.urls')),
  path('auth/', include('djoser.urls.jwt')),
  path('silk/', include('silk.urls', namespace='silk')),

  re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
  path('admin/', admin.site.urls),
  path('products', include('products.urls')),
  path('cart/', include('carts.urls')),
  path('orders/', include('orders.urls')),
  path('wishlist/', include('wishlists.urls')),
  path('shipping-addresses', include('users.urls')),
  path('reviews/', include('reviews.urls')),
]

urlpatterns += [path(r'^i18n/', include('django.conf.urls.i18n')),]
urlpatterns += i18n_patterns(path(r'^admin/', admin.site.urls))


# let's design the api for our e-commerce app
# 1. Products
# 2. Users
# 3. Reviews
# 4. Orders
# 5. Payments
# 6. Shipping
# 7. Coupons
# 8. Categories
# 9. Brands
# 10. Cart
# 11. Wishlist
# 12. Addresses


"""
Customers use cases:-
1. View products
2. (Add/Remove/Increase Quantity) products to cart
3. (Add/Remove) products to wishlist
4. View cart
5. View wishlist
6. Place order
7. View orders
8. View order details
9. Cancel order
10. Return order
11. Rate product (Review) 
12. View reviews for a product
13. View profile
14. Update profile
15. Change password
16. Add/Remove/View shipping address
17. Add/Remove/View billing address
19. Apply coupon
21. View products by (category, brand, price range, rating, etc)
22. Search products by name and add any filter available like category, brand, price range, rating, etc

Seller use cases:-
1. Add/Update/Delete products
2. View products
3. View orders
4. View order details
5. View reviews for a product
6  View reviews for him as a seller
6. View/Update his profile

"""


"""
1. Products:-

  /products/ -> GET, POST
  /products/<id>/ -> GET, PUT, DELETE
  
  /products/<id>/variants/ -> GET, POST
  /products/<id>/variants/<id>/ -> GET, PUT, DELETE
  
2. Carts:-
    /cart/ -> GET, POST
    /cart/<id>/ -> GET, PUT, DELETE
  
3. Orders:-
    /orders/ -> GET, POST
    /orders/<id>/ -> GET, PUT

4. wishlist:-
    /wishlist/ -> GET, POST
    /wishlist/<id>/ -> GET, DELETE
"""