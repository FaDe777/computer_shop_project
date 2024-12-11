from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import *

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин',widget=forms.TextInput(attrs={'class':'form-input'}))
    email = forms.EmailField(label='Email',widget=forms.EmailInput(attrs={'class':'form-input'}))
    password1 = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class':'form-input'}))
    password2 = forms.CharField(label='Повтор пароля',widget=forms.PasswordInput(attrs={'class':'form-input'}))

    class Meta:
        model = User
        fields = ('username','email','password1','password2')

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин',widget=forms.TextInput(attrs={'class':'form-input'}))
    password = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class':'form-input'}))

    error_messages = {
        "invalid_login": "Неверный логин или пароль"
    }

    class Meta:
        model = User
        fields = ('username','password')

class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label='Новая почта',widget=forms.EmailInput())

# class ChangePasswordForm(PasswordChangeForm):


class ReviewForm(forms.ModelForm):
    rates = (
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5)
    )

    rate = forms.ChoiceField(label='Оценка',choices=rates,widget=forms.RadioSelect())
    advantages = forms.CharField(label='Достоинства',widget=forms.Textarea(attrs={'class':'review-fields'}))
    disadvantages = forms.CharField(label='Недостатки',widget=forms.Textarea(attrs={'class': 'review-fields'}))
    text = forms.CharField(label='Комментарий',widget=forms.Textarea(attrs={'class':'review-fields'}))

    class Meta:
        model = Reviews
        fields = ('rate','advantages','disadvantages','text')

class Ordering(forms.ModelForm):
    name = forms.CharField(label='Имя', error_messages={'required': ''}, widget=forms.TextInput(attrs={'class':'order-input'}))
    surname = forms.CharField(label='Фамилия', error_messages={'required': ''}, widget=forms.TextInput(attrs={'class':'order-input'}))
    phone = forms.CharField(label='Телефон', error_messages={'required': ''},widget=forms.NumberInput(attrs={'class':'order-input'}))
    email = forms.CharField(label='Email(сюда придёт код)', error_messages={'required': ''}, widget=forms.EmailInput(attrs={'class':'order-input'}))
    address = forms.CharField(label='Адрес',error_messages={'required': ''}, widget=forms.Textarea(attrs={'placeholder':'Город, улица, дом, подъезд, этаж, номер квартиры','class':'address-input'}))

    class Meta:
        model = Order
        fields = ('name','surname','phone','email','address')

class OrderCheck(forms.Form):
    phone = forms.CharField(label = 'Номер телефона',widget=forms.NumberInput(attrs={'autocomplete':'on','placeholder':'Номер телефона','class':'order-input'}))
    order_id = forms.IntegerField(label = 'Номер заказа',widget=forms.NumberInput(attrs={'placeholder':'Номер заказа','class':'order-input'}))

    def clean(self):
        cleaned_data = super().clean()
        pk = cleaned_data.get('order_id')
        phone = cleaned_data.get('phone')
        if not (Order.objects.filter(pk = pk).exists() and Order.objects.filter(phone = phone)):
            raise ValidationError('Поля заполнены некорректно')


class Filter(forms.Form):

    min_price = forms.IntegerField(label='От', required = False)
    max_price = forms.IntegerField(label='До', required = False)

    a = forms.BooleanField(label='Android', required = False)
    b = forms.BooleanField(label='IOS', required = False)


class AvatarLoader(forms.ModelForm):

    avatar = forms.ImageField(widget = forms.FileInput())

    class Meta:
        model = UserCustom
        fields = ('avatar',)

class ReplyForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'class':'reply-form','placeholder': 'Написать комментарий...'}))

    class Meta:
        model = Reply
        fields = ('text',)