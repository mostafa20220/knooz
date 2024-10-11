from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
class ProductReview(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    customer = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='reviews_set' ,null=True)
    seller = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='products_review_set', null=True)
    rating = models.IntegerField() # min=1, max=5
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.customer == self.seller:
            raise ValidationError("Customer and seller cannot be the same user.")
        super().save(*args, **kwargs)


    def __str__(self):
        # handle if customer is None
        review = f'Review for: {self.product.name}'
        if self.customer:
            review += f' by {self.customer.email}'
        return review