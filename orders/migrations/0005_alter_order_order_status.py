# Generated by Django 5.1.2 on 2024-11-03 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_order_payment_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('placed', 'Placed'), ('cancelled', 'Cancelled'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('returned', 'Returned'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
    ]
