# Generated by Django 5.1.1 on 2024-10-10 10:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_brand_name_alter_category_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='variantimage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('name', 'seller', 'brand')},
        ),
        migrations.AlterUniqueTogether(
            name='productvariant',
            unique_together={('product', 'size', 'color')},
        ),
    ]
