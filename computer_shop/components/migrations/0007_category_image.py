# Generated by Django 5.0.4 on 2024-06-27 18:02

import components.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0006_alter_reviews_dislikes_alter_reviews_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(null=True, upload_to=components.utils.category_image_path),
        ),
    ]