# Generated by Django 5.0.4 on 2024-06-28 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0008_alter_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(max_length=50, null=True, verbose_name='Email покупателя'),
        ),
    ]