from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint, Q
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import *
from django.dispatch.dispatcher import receiver
from .utils import *

class UserCustom(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom')
    avatar = models.ImageField(upload_to='photos/%Y/%m/%d/')
    email_verify = models.BooleanField(null=True)


class Components(models.Model):
    title = models.CharField(max_length = 200,verbose_name = "Товар")
    slug = models.SlugField(max_length=255,unique=True,db_index=True,verbose_name="URL",null=True)
    price = models.IntegerField(null=True, verbose_name='Цена')
    options = models.JSONField(blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    quantity = models.PositiveSmallIntegerField(null=True)
    in_stock = models.BooleanField(null=True)
    cat = models.ForeignKey('Category', on_delete=models.PROTECT,db_index=True,null=True,verbose_name='Категория')

    def get_absolute_url(self):
        return reverse('component',kwargs={'component_slug':self.slug,'category_slug':self.cat.slug})

    def __str__(self):
        return self.title

    def rating(self):
        return round(sum([i.rate for i in self.reviews.all()]) / len(self.reviews.all()),1)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = "Товары"

class ComponentImages(models.Model):
    component = models.ForeignKey(Components,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to=component_path)

class Category(models.Model):
    c_name = models.CharField(max_length = 100,verbose_name='Категории')
    image = models.ImageField(upload_to=category_image_path,null=True,blank=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL",null=True)

    def get_absolute_url(self):
        return reverse('components',kwargs={'category_slug':self.slug})

    def __str__(self):
        return self.c_name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='cart')

class CartItem(models.Model):
    cart = models.ForeignKey('Cart',on_delete=models.CASCADE,related_name='items')
    item = models.ForeignKey('Components',on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)


class Reviews(models.Model):
    advantages = models.TextField(blank=True,max_length=1000,verbose_name='Достоинства')
    disadvantages = models.TextField(blank=True, max_length=1000,verbose_name='Недостатки')
    text = models.TextField(blank=True, max_length=1000,verbose_name="Текст комментария")
    create_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, verbose_name = 'Автор')
    component = models.ForeignKey('Components', on_delete=models.CASCADE, verbose_name='Товар',related_name='reviews', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='comment_likes',blank=True)
    dislikes = models.ManyToManyField(User,related_name='comment_dislikes',blank=True)
    rate = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [CheckConstraint(check=Q(rate__range = (1,5)),name='rate_valid'),
            UniqueConstraint(fields=['author','component'],name='rate_once')]
        ordering = ('-create_date',)


    def liked(self,r):
        return self.likes.filter(pk=r.user.id).exists()

    def likes_count(self):
        return self.likes.count()

    def dislikes_count(self):
        return self.dislikes.count()

    def reply_count(self):
        return self.replies.count()

    def count(self):
        return self.count()

class Reply(models.Model):
    review = models.ForeignKey('Reviews',on_delete=models.CASCADE,related_name='replies',verbose_name='Отзыв')
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='replies_author',verbose_name='Автор')
    text = models.TextField(max_length=500,verbose_name='Текст')
    time_create = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering=('time_create',)

class Order(models.Model):
    name = models.CharField(max_length = 20, verbose_name='Имя покупателя')
    surname = models.CharField(max_length = 20, verbose_name="Фамилия покупателя")
    phone = models.CharField(max_length = 20, verbose_name='Телефон покупателя')
    email = models.EmailField(max_length=50, verbose_name='Email покупателя', null=True)
    address = models.TextField(verbose_name='Адрес покупателя')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания заказа")
    status = models.CharField(max_length=50,choices=(('1','Ждёт отправки'),('2','В пути'),('3','Доставлен')))

    def get_absolute_url(self):
        return reverse('order_status',kwargs={'number':self.phone,'id':self.pk})

    def count(self):
        return self.items.count()

    def total(self):
        total = 0
        for i in self.items.all():
            total += i.item.price * i.quantity
        return total

    def __str__(self):
        return f'Заказ №{self.pk}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Components, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def summ(self):
        return self.item.price * self.quantity

class Notifications(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


# class SearchFilterType(models.Model):
#
#     CHECKBOX = 'checkbox'
#     RADIO = 'radiobutton'
#
#     HTML_TYPE_CHOICES = (
#         (CHECKBOX,'Чекбокс'),
#         (RADIO,'Радиокнопка')
#     )
#
#     key = models.CharField('Ключ поиска',max_length=50,choices=HTML_TYPE_CHOICES,default=CHECKBOX)
#     html_code = models.TextField('HTML код для страницы фильтрации')
#
#     class Meta:
#         verbose_name = 'Тип поиска при фильтрации'
#         verbose_name_plural = 'Типы поиска при фильтрации'
#
#     def __str__(self):
#         return f"{self.get_key_display()}"
#
# class SpecCategoryName(models.Model):
#     category = models.ForeignKey(Category,on_delete=models.CASCADE,verbose_name='Категория')
#     name = models.CharField('Название характеристики',max_length=100)
#     key = models.CharField('Ключ характеристики',max_length=100)
#     search_filter_type = models.ForeignKey(SearchFilterType,on_delete=models.CASCADE,verbose_name='Тип фильтра для поиска')
#     use_in_shortlist = models.BooleanField('Использование в превью',default=False)
#
#     class Meta:
#         unique_together = ('category','name','key')
#         verbose_name='Категория характеристики'
#         verbose_name_plural = 'Категории характеристик'
#
#     def __str__(self):
#         return f"Характеристики категории - {self.category.c_name} | {self.name}"
#
# class Spec(models.Model):
#     INT = 'int'
#     STR = 'str'
#     FLOAT = 'float'
#     BOOL = 'bool'
#
#     TYPE_CHOICES = (
#         (INT,'Целое число'),
#         (STR,'Строка'),
#         (FLOAT,'Десятичная дробь'),
#         (BOOL,'Булевое значение')
#     )
#
#     category = models.ForeignKey(Category,on_delete=models.CASCADE,verbose_name="Категория характеристик",related_name='category_specs')
#     spec_category = models.ForeignKey(SpecCategoryName,on_delete=models.CASCADE,verbose_name='Название категории характеристики',related_name='specnames')
#     product = models.ForeignKey(Components,on_delete=models.CASCADE,verbose_name='Товар',related_name='product_specs',null=True,blank=True)
#     spec_unit = models.ForeignKey('SpecUnit',on_delete=models.CASCADE,verbose_name='Единица измерения',null=True,blank=True)
#     value = models.CharField('Значение характеристики',max_length=100)
#     var_type = models.CharField('Тип значения',max_length=100,choices=TYPE_CHOICES,null=True,blank=True)
#
#     class Meta:
#         unique_together = ('category','spec_category','product','value')
#         verbose_name = 'Характеристика товара'
#         verbose_name_plural='Характеристики товаров'
#
#     def __str__(self):
#         return " | ".join([
#             self.category.c_name,
#             self.spec_category.name,
#             self.spec_category.key,
#             self.value
#         ])
#
# class SpecUnit(models.Model):
#     category = models.ForeignKey(Category,on_delete=models.CASCADE,verbose_name='Категория характеристики')
#     name = models.CharField('Название',max_length=100)
#     unit = models.CharField('Единица измерения',max_length=10)
#
#     class Meta:
#         unique_together = ('category','name','unit')
#         verbose_name = 'Единица измерения характеристики'
#         verbose_name_plural = 'Единицы измерения характеристик'
#
#     def __str__(self):
#         return f"Единица измерения характеристики - {self.category.c_name} | {self.name} | {self.unit}"
#
# class SpecUnitValidation(models.Model):
#     INT = 'int'
#     STR = 'str'
#     FLOAT = 'float'
#     BOOL = 'bool'
#
#     TYPE_CHOICES = (
#         (INT,'Целое число'),
#         (STR,'Строка'),
#         (FLOAT,'Десятичная дробь'),
#         (BOOL,'Булевое значение')
#     )
#
#     specunit = models.ForeignKey(SpecUnit,on_delete=models.CASCADE,verbose_name='Единица измерения')
#     name = models.CharField('Имя единицы измерения для валидации',max_length=100)
#     var_type = models.CharField('Тип значения',max_length=100,choices=TYPE_CHOICES)
#
#     class Meta:
#         unique_together = ('specunit','name','var_type')
#         verbose_name = 'Валидация единицы измерения товара'
#         verbose_name_plural = 'Валидации единиц измерения товаров'
#
#     def __str__(self):
#         return f"Валидация {self.specunit}"






