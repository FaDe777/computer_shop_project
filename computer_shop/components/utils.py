from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import *

menu = [{'title': 'Главная','url_n': 'home','selected_index': 0},{'title': 'О сайте','url_n': 'about','selected_index': 1},{'title':'Корзина','url_n':'cart','selected_index': 2}]

def send_email_verify(request,user):
    current_site = get_current_site(request)
    context = {'user':user,'domain': current_site.domain,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token': default_token_generator.make_token(user)}
    message = render_to_string('components/verify_email.html',context=context)
    email = EmailMessage('Загаловок',message,to=[user.email])
    email.send()

def code_validation(request,code):
    print(type(request.session['code']),type(code))
    if request.session['code'] == int(code):
        return True
    else:
        return False

def component_path(instance,filename):
    return f'photos/components/{instance.component.title}/{filename}'

def category_image_path(instance,filename):
    return f'photos/category/{instance.c_name}/{filename}'

def addons_finder():
    pass
#class DataMixin:
    #def get_user_context(self,**kwargs):






