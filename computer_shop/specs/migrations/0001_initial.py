# Generated by Django 5.0.4 on 2024-07-04 22:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('components', '0011_alter_order_options_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchFilterType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('checkbox', 'Чекбокс'), ('radiobutton', 'Радиокнопка')], default='checkbox', max_length=50, verbose_name='Ключ поиска')),
                ('html_code', models.TextField(verbose_name='HTML код для страницы фильтрации')),
            ],
            options={
                'verbose_name': 'Тип поиска при фильтрации',
                'verbose_name_plural': 'Типы поиска при фильтрации',
            },
        ),
        migrations.CreateModel(
            name='SpecCategoryName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название характеристики')),
                ('key', models.CharField(max_length=100, verbose_name='Ключ характеристики')),
                ('use_in_shortlist', models.BooleanField(default=False, verbose_name='Использование в превью')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='components.category', verbose_name='Категория')),
                ('search_filter_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specs.searchfiltertype', verbose_name='Тип фильтра для поиска')),
            ],
            options={
                'verbose_name': 'Категория характеристики',
                'verbose_name_plural': 'Категории характеристик',
                'unique_together': {('category', 'name', 'key')},
            },
        ),
        migrations.CreateModel(
            name='SpecUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('unit', models.CharField(max_length=10, verbose_name='Единица измерения')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='components.category', verbose_name='Категория характеристики')),
            ],
            options={
                'verbose_name': 'Единица измерения характеристики',
                'verbose_name_plural': 'Единицы измерения характеристик',
                'unique_together': {('category', 'name', 'unit')},
            },
        ),
        migrations.CreateModel(
            name='Spec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100, verbose_name='Значение характеристики')),
                ('var_type', models.CharField(blank=True, choices=[('int', 'Целое число'), ('str', 'Строка'), ('float', 'Десятичная дробь'), ('bool', 'Булевое значение')], max_length=100, null=True, verbose_name='Тип значения')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_specs', to='components.category', verbose_name='Категория характеристик')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_specs', to='components.components', verbose_name='Товар')),
                ('spec_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specnames', to='specs.speccategoryname', verbose_name='Название категории характеристики')),
                ('spec_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='specs.specunit', verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Характеристика товара',
                'verbose_name_plural': 'Характеристики товаров',
                'unique_together': {('category', 'spec_category', 'product', 'value')},
            },
        ),
        migrations.CreateModel(
            name='SpecUnitValidation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя единицы измерения для валидации')),
                ('var_type', models.CharField(choices=[('int', 'Целое число'), ('str', 'Строка'), ('float', 'Десятичная дробь'), ('bool', 'Булевое значение')], max_length=100, verbose_name='Тип значения')),
                ('specunit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specs.specunit', verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Валидация единицы измерения товара',
                'verbose_name_plural': 'Валидации единиц измерения товаров',
                'unique_together': {('specunit', 'name', 'var_type')},
            },
        ),
    ]
