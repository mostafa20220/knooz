from unicodedata import category

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from products.models import Product, Brand, Category
from django.urls import reverse

from users.models import User


# Create your tests here.
class ProductsViewsTest(APITestCase):
    def setUp(self):

        # create seller user to create, update, delete products

        self.user =  User.objects.create_user(
            email="mh@holouly.com",
            password="passwordd",
            user_type="SELLER",
        )

        self.client.force_authenticate(user=self.user)




        # self.client =  APIClient()
        self.list_url = reverse('products:product-list')
        self.detail_url = reverse('products:product-detail', args=[1])

        self.brand=Brand.objects.create(name='Brand 1')
        self.category=Category.objects.create(name='Category 1')
        self.product = {
            'name': 'Product 1',
            'description': 'Product 1 description',
            'category': self.category.id,
            'brand': self.brand.id,
            'variants': [
            {
            'price': 1000,
            'stock': 10,
            'color': 'Red',
            'size': 'XL'
            },
            {
            'price': 1500,
            'stock': 5,
            'color': 'Blue',
            'size': 'L'
            }
        ]
        }


    def test_create_product_with_variants(self):
        response = self.client.post(self.list_url, self.product, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Product 1')
        self.assertEqual(Product.objects.get().variants.count(), 2)


    def test_list_products(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 0)