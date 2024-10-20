from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from core.models import BaseTimeStamp


def validate_rating(value):
    if not 1 <= value <= 5:
        raise ValidationError('Rating must be between 1 and 5.')

# Create your models here.
class ProductReview(BaseTimeStamp):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,related_name='reviews')
    customer = models.ForeignKey('users.User', on_delete=models.SET_NULL,related_name='reviews' ,null=True)
    seller = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='products_reviews', null=True)
    rating = models.IntegerField(validators=[validate_rating]) # min=1, max=5
    review = models.TextField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'customer'], name='unique_review', violation_error_message='You have already reviewed this product.')
        ]
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

class CustomerReviewsLikes(models.Model):
    review = models.ForeignKey('reviews.ProductReview', on_delete=models.CASCADE, related_name='likes')
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['review', 'customer'], name='unique_like')
        ]

    def __str__(self):
        return f'{self.customer.email} likes {self.review.product.name} review'