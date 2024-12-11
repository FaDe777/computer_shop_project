from django.contrib.auth import logout, authenticate, get_user
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.views.generic import ListView, CreateView
from django.contrib import messages
import random
from django.views import View
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
# from smsaero import SmsAero
from computer_shop import settings
# from .custom_permissions import IsAdminOrReadOnly
# from .serializers import ComponentsSerializer
from .utils import *
from .forms import *
from rest_framework import generics, viewsets
from django.forms import model_to_dict
import datetime
from . import tasks
from django.db.models import Q

menu = [{'title': 'Главная','url_n': 'home','selected_index': 0},{'title': 'О сайте','url_n': 'about','selected_index': 1},{'title':'Корзина','url_n':'cart','selected_index': 2},
        {'title': 'Статус заказа','url_n':'check_order_status','selected_index':6}]


def home(request):
    categories = Category.objects.all()
    posts = Components.objects.all()

    paginator = Paginator(categories,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if not request.session.get('cart'):
        request.session['cart'] = {}
    request.session['cart'] = request.session['cart']
    #request.session['cart'].clear()

    keys = list(map(int,request.session.get('cart').keys()))

    # tasks.test.delay()

    return render(request,'components/index.html',{'menu':menu,'categories': categories,'keys': keys,'posts':posts,'page_obj':page_obj,'menu_selected': 0})


def about(request):
    categories = Category.objects.all()
    return render(request,'components/about.html',{'menu':menu,'categories': categories,'menu_selected': 1})

# class Login(LoginView):
#     categories = Category.objects.all()
#     form_class = LoginUserForm
#     template_name = 'components/login.html'
#     extra_context = {'menu':menu,'title':'Авторизация','categories': categories,'menu_selected': 3}
#     def get_success_url(self):
#         return reverse_lazy('home')

def login(request):
    if request.method == "POST":
        form = LoginUserForm(data=request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                auth.login(request,user)
                return HttpResponseRedirect(reverse('home'))
    else:
        form = LoginUserForm()

    context = {'menu':menu,'title':'Авторизация','menu_selected': 3,'form':form}
    return render(request,'components/login.html',context)

# class Login(View):
#     def get(self,request):
#         form = LoginUserForm()
#         return render(request, 'components/login.html', {'menu':menu,'form':form})
#
#     def post(self,request):
#         form = LoginUserForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = authenticate(username=username, password=password)
#             if user:
#                 auth.login(request,user)
#                 return HttpResponseRedirect(reverse('home'))
#         return render(request, 'components/login.html', {'menu': menu, 'form': form})

def register(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = RegisterUserForm(data = request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            UserCustom.objects.create(user=user)
            #send_email_verify(request,user)
            return redirect('confirm_email')
    else:
        form = RegisterUserForm()
    return render(request,'components/register.html',{'menu':menu,'form':form,'categories': categories,'menu_selected': 4})

class EmailVerify(View):
    def get(self,request,uidb64,token):
        user = self.get_user(uidb64)
        if user is not None and default_token_generator.check_token(user,token):
            auth.login(request,user)
            return redirect('home')
        return redirect('register')

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

def logout_user(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER'))

def cart(request):
    if not request.session.get('cart'):
          request.session['cart'] = dict()
    categories = Category.objects.all()
    cart = [(Components.objects.get(pk = i),j) for i,j in request.session['cart'].items()]
    result = sum([int(i[0].price)*i[1] for i in cart])
    count = sum((i[1] for i in cart))
    return render(request,'components/cart.html',{'menu':menu,'categories': categories,'cart': cart, 'result':result,'count':count, 'menu_selected': 2})

def cart_add_ajax(request):
    component_id = request.POST.get('value')

    if not request.session.get('cart'):
          request.session['cart'] = dict()
          cart = request.session['cart']
    else:
          request.session['cart'] = request.session['cart']
          cart = request.session['cart']

    if not cart.get(str(component_id),None):
        cart[str(component_id)] = 1
    else:
        if request.POST.get('name') == "minus":
            if cart[str(component_id)] > 1:
                cart[str(component_id)] -= 1
        else:
            if Components.objects.get(pk=component_id).quantity > cart[str(component_id)]:
                cart[str(component_id)] += 1
    response = {

        'total': cart[component_id],
        'price': '{0:,}'.format(Components.objects.get(pk=component_id).price * cart[component_id]).replace(',', ' ') + " ₽",
        'id': str(component_id),
        'sum': str(sum([Components.objects.get(pk=i[0]).price*i[1] for i in cart.items()])) + " ₽",
        'count': str(sum([i[1] for i in cart.items()])) + " шт."
    }

    return JsonResponse(response)

def cart_del(request):
    component_id = request.POST.get('value')
    request.session['cart'] = request.session['cart']
    del request.session['cart'][str(component_id)]



    response={
        'len': len(request.session['cart']),
        'sum': str(sum([Components.objects.get(pk=i[0]).price * i[1] for i in request.session['cart'].items()])) + " ₽",
        'count': str(sum([i[1] for i in request.session['cart'].items()])) + " шт."
    }

    return JsonResponse(response)

def clear_cart(request):
    request.session['cart'] = request.session['cart']
    request.session['cart'].clear()
    return HttpResponseRedirect(reverse('cart'))

# def user(request,user):
#     user = User.objects.get(username=user)
#
#     form = AvatarLoader(request.POST)
#     return render(request, 'components/profile.html', {'menu':menu,'user':user,'menu_selected': 5})

class UserProfile(View):

    def get(self, request, user):
        user = User.objects.get(username=user)
        form = AvatarLoader()
        return render(request, 'components/profile.html', {'menu':menu,'user':user,'form':form,'menu_selected': 5})

    def post(self,request,user):
        user = User.objects.get(username=user)
        if request.POST.get('delete'):
            user.custom.avatar.delete()
            form = AvatarLoader()
        else:
            form = AvatarLoader(request.POST,request.FILES)
            if form.is_valid():
                obj = UserCustom.objects.get(user=user)
                obj.avatar = form.cleaned_data['avatar']
                obj.save()
        return render(request,'components/profile.html', {'menu':menu,'user':user,'form':form,
         'menu_selected': 5})

class ProfileSettings(View):
    def get(self,request):
        return render(request,'components/profile_settings.html',{'menu':menu,'user':request.user})

def notifications(request):
    notifications = Notifications.objects.all()
    return render(request,'components/notifications.html',{'menu':menu,'notifications':notifications})

class ChangeEmail(View):
    def get(self,request):
        form = ChangeEmailForm()
        return render(request, 'components/change_email.html', {'menu': menu,'form':form})
    def post(self,request):
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            if request.POST.get('code'):
                if code_validation(request,request.POST.get('code')):
                    request.user.email = request.session['email']
                    request.user.save()
                    return redirect('home')
                else:
                    messages.error(request, 'неправильный код')
                    return render(request, 'components/change_email.html',
                                  {'menu': menu, 'form': form, 'code_required': True})
            else:
                code = random.randint(1,100)
                request.session['code'] = code

                request.session['email'] = form.cleaned_data['new_email']
                mail = EmailMessage('Код подтверждения',str(code),to=[form.cleaned_data['new_email']])
                mail.send()
                return render(request, 'components/change_email.html',
                              {'menu': menu, 'form': form, 'code_required': True})
        return render(request, 'components/change_email.html', {'menu': menu,'form':form,'code_required': False})



class ChangePassword(View):
    def get(self,request):
        form = PasswordChangeForm(request.user)
        return render(request,'components/change_password.html',{'menu':menu,'form':form})

    def post(self,request):
        form = PasswordChangeForm(request.user,request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        return render(request, 'components/change_password.html', {'menu': menu, 'form': form})

def list_components(request, category_slug):
    categories = Category.objects.all()
    category = Category.objects.get(slug=category_slug)
    posts = Components.objects.filter(cat_id = category.pk)
    form = Filter(request.GET)

    if form.is_valid():
        if form.cleaned_data['min_price']:
            posts = posts.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data['max_price']:
            posts = posts.filter(price__lte=form.cleaned_data['max_price'])
        if form.cleaned_data['a']:
            posts = posts.filter(**{'options__Операционная система':'Android'})
        if form.cleaned_data['b']:
            posts = posts.filter(**{'options__Операционная система':'IOS'})


    keys = list(map(int, request.session['cart'].keys()))
    return render(request,'components/components.html',{'menu':menu,'posts': posts,'categories': categories,'keys':keys,'category': category,'form':form,'category_selected': category.pk})

def show_component(request,category_slug,component_slug):
    component_object = Components.objects.get(slug=component_slug)
    options = component_object.options

    comments = Reviews.objects.filter(component=component_object)
    select_opt = Components.objects.filter(title__contains=component_object.options['titlecore'])
    addons = component_object.options['addons']
    dct = {}


    for i in addons:
        query = select_opt.filter(options__addons__has_key=i)  #select_opt.filter(options__contains=i)
        var = set([j.options['addons'][i] for j in query])
        lst = []
        for j in var:
            stack = query.filter(**{f"options__addons__{i}":j}) #[h for h in query if h.options['addons'][i]==j]
            if len(stack) == 1:
                lst.append(stack[0])
                continue
            second = stack[1]
            for h in addons:
                if i != h:
                    a = component_object.options['addons'][h]
                    stack = stack.filter(**{f"options__addons__{h}":a}) #[g for g in stack if a==g.options['addons'][h]]
            if stack:
                lst.append(stack[0])
            else:
                lst.append(second)
        dct[i] = lst

    if request.session.get('cart'):
        keys = list(map(int, request.session['cart'].keys()))
    else:
        keys = []

    if request.method == 'POST' and not request.POST.get('value',0):
        if request.POST.get('rate',0):
            comment_form = ReviewForm(data=request.POST)
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.component = component_object
            new_comment.save()
            form_reply = ReplyForm()
        else:
            # print(request.POST)
            # form_reply = ReplyForm(data=request.POST)
            # new_reply = form_reply.save(commit=False)
            # new_reply.author = request.user
            # new_reply.review = Reviews.objects.get(id=request.POST['reply'])
            # form_reply.save()
            form_reply = ReplyForm()
            comment_form = ReviewForm()
    else:
        form_reply = ReplyForm()
        comment_form = ReviewForm()

    return render(request,'components/show_component.html',{'menu':menu,'component': component_object,
                                                            'options': options,'form': comment_form,'form_reply':form_reply,'comments':comments, 'keys': keys,'select_opt':dct})

def reply_ajax(request):
    print(request.POST)
    form = ReplyForm(data=request.POST)
    new_reply = form.save(commit=False)

    new_reply.author = request.user
    new_reply.review = Reviews.objects.get(id=request.POST['val'])
    new_reply.save()

    if request.user.custom.avatar:
        img = 'True'
        src = request.user.custom.avatar.url
    else:
        img = 'False'
        src = ''

    response = {'data': request.POST,'id':request.POST['val'],'img':img,'src':src}
    return JsonResponse(response)

def reply_delete_ajax(request):
    pk = int(request.POST['val'])
    reply = Reply.objects.get(pk=pk)
    count = reply.review.reply_count() - 1
    r_id = reply.review.pk
    reply.delete()
    response={'pk':pk,'count':count,'r_id':r_id}
    return JsonResponse(response)

def search(request):
    categories = Category.objects.all()
    text = request.GET.get('s')
    if text:
        posts = Components.objects.filter(title__icontains=text)
        return render(request, 'components/search.html', {'menu':menu,'categories': categories,'posts': posts})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# def comment(request,comment_pk):
#     comment = Reviews.objects.get(pk=comment_pk)
#     likes_connected = comment
#     liked = False
#     if likes_connected.likes.filter(pk=request.user.id).exists():
#         liked = True
#     likes_count = likes_connected.likes_count()
#     comment_is_liked = liked
#     return render(request, 'components/comment.html',{'comment': comment, 'likes_count':likes_count, 'comment_is_liked': comment_is_liked})
#
def comment_like(request):

    comment = Reviews.objects.get(id=request.POST.get('value'))

    re_dis = False
    re_like = False

    likes = comment.likes_count()
    dislikes = comment.dislikes_count()

    if request.POST.get('type') == 'like':
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
            act = 'False'
            likes -= 1
        else:
            act = 'True'
            comment.likes.add(request.user)
            if comment.dislikes.filter(id=request.user.id).exists():
                comment.dislikes.remove(request.user)
                dislikes -=1
                re_dis = 'True'
            likes += 1
    else:
        if comment.dislikes.filter(id=request.user.id).exists():
            comment.dislikes.remove(request.user)
            act = 'False'
            dislikes -=1
        else:
            act = 'True'
            comment.dislikes.add(request.user)
            if comment.likes.filter(id=request.user.id).exists():
                comment.likes.remove(request.user)
                re_like = 'True'
                likes -= 1
            dislikes +=1

    response = {'likes':likes,'dislikes':dislikes,'pk': comment.pk,'act':act,'re_like':re_like,'re_dis':re_dis}
    return JsonResponse(response)



#    def get_queryset(self):
#        return Components.objects.filter(title__icontains=self.request.GET.get('q'))

#    def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args,**kwargs)
#         context['q'] = self.request.GET.get['q']
#         return context

# def reviews(request, category_slug, component_slug):
#     component_object = Components.objects.get(slug=component_slug)
#     comments = Comments.objects.filter(component=component_object, parent__isnull=True)
#
#     if request.method == 'POST':
#         comment_form = CommentForm(data=request.POST)
#         new_comment = comment_form.save(commit=False)
#         new_comment.author = request.user
#         new_comment.component = component_object
#         if request.POST.get('reply'):
#             parent_id = request.POST.get('reply')
#             new_comment.parent = Comments.objects.get(pk=parent_id)
#         else:
#             new_comment.save()
#     else:
#         comment_form = CommentForm()
#
#     return render(request, 'components/reviews.html',
#                   {'menu': menu, 'component': component_object, 'form': comment_form,
#                    'comments': comments, 'category_slug': category_slug, 'component_slug': component_slug, 'nav_select': 2})

def ordering(request):

    count = sum([i for i in request.session['cart'].values()])
    result = sum([Components.objects.get(pk=i[0]).price * i[1] for i in request.session['cart'].items()])

    if str(count)[-1] in ('0', '5', '6', '7', '8', '9') or str(count)[-2:] in [str(i) for i in range(11, 20)]:
        word = 'товаров'
    elif str(count)[-1] == '1' and (len(str(count)) == 1 or len(str(count)) >= 3):
        word = 'товар'
    else:
        word = 'товара'


    if request.method == 'POST':
        request.session['cart'] = request.session['cart']
        form = Ordering(request.POST)
        if form.is_valid():
            context = {'menu': menu, 'form': form, 'count': count, 'result': result, 'word': word, 'otp_required': True}
            if request.POST.get('otp'):
                if otp_verify(request):
                    return redirect('home')
                else:
                    return render(request, 'components/ordering.html',
                                  {'menu': menu, 'form': form, 'count': count, 'result': result, 'word': word,
                                   'otp_required': True})
            else:
                otp = str(random.randint(100,500))
                request.session['name'] = form.cleaned_data['name']
                request.session['surname'] = form.cleaned_data['surname']
                request.session['phone'] = int(form.cleaned_data['phone'])
                request.session['email'] = form.cleaned_data['email']
                request.session['address'] = form.cleaned_data['address']
                # request.session['end_date'] = datetime.datetime.now() + datetime.timedelta(days=random.randint(2,5))
                request.session['otp'] = otp

                send_mail('Код подтверждения',otp,settings.EMAIL_HOST_USER,[form.cleaned_data['email']])

                return render(request,'components/ordering.html',{'menu':menu,'form':form,'count':count,'result':result,'word':word,'otp_required':True})

        # order = form.save()
        # cart = [(Components.objects.get(pk = i),j) for i,j in request.session['cart'].items()]
        # for i in cart:
        #     OrderItem.objects.create(order=order,item = i[0],quantity = i[1])
        # del request.session['cart']

    else:
        form = Ordering()

    return render(request,'components/ordering.html',{'menu':menu,'form':form,'count':count,'result':result,'word':word,'otp_required':False})

def otp_verify(request):
    submitted_otp = request.POST.get('otp')
    saved_otp = request.session.get('otp')
    if submitted_otp == saved_otp:
        request.session['cart'] = request.session['cart']
        order = Order.objects.create(name=request.session['name'],surname=request.session['surname'],phone=request.session['phone'],email=request.session['email'],address=request.session['address'],status=1)
        cart = [(Components.objects.get(pk=i), j) for i, j in request.session['cart'].items()]
        for i in cart:
            OrderItem.objects.create(order=order,item = i[0],quantity = i[1])
        del request.session['cart']
        return True
    else:
        return False


# def send_sms(phone,message):
#     api = SmsAero(settings.SMSAERO_EMAIL, settings.SMSAERO_API_KEY)
#     res = api.send(phone,message)
#     assert res.get('success'), res.get('message')
#     return res.get('data')

def check_order_status(request):
    if request.method == 'POST':
        form = OrderCheck(request.POST)
        if form.is_valid():
            return redirect(reverse('order_status',args=((form.cleaned_data['phone'],form.cleaned_data['order_id'],))))
    else:
        form = OrderCheck()

    return render(request,'components/check_order_status.html',{'menu':menu,'form':form,'menu_selected': 6})

def order_status(request,number,id):
    order = Order.objects.get(pk=id,phone=number)
    main = ['Фото','Название','Кол-во','Цена за штуку','Общая цена']
    inf = ['ФИО', 'Телефон', 'Адрес']
    return render(request,'components/order_status.html',{'menu':menu,'id':id,'items':order.items.all(),'main':main,'inf':inf,'order':order})

def orders(request):
    orders = Order.objects.filter(status=True)
    main = ['Дата создания','Номер заказа','Кол-во позиций','Сумма']
    return render(request,'components/orders.html',{'menu':menu,'orders':orders,'main':main})

def orders_completed(request):
    orders = Order.objects.filter(status=3)
    main = ['Дата создания', 'Номер заказа', 'Кол-во позиций', 'Сумма']
    return render(request, 'components/orders_completed.html', {'menu': menu, 'orders': orders, 'main': main})

# class ComponentsAPIView(generics.ListAPIView):
#     queryset = Components.objects.all()
#     serializer_class = ComponentsSerializer

# class ComponentsAPIView(APIView):
#
#     def get(self,request):
#         objects = Components.objects.all()
#         data = ComponentsSerializer(objects, many=True).data
#         return Response({'posts': data})
#
#     def post(self,request):
#         serializer = ComponentsSerializer(data=request.data)
#         serializer.is_valid()
#         serializer.save()
#         data = serializer.data
#         return Response({'new_obj': data})
#
#     def put(self, request, *args, **kwargs):
#         pk = kwargs.get('pk', None)
#         if not pk:
#             return Response({'error': 'Метод пут не определён'})
#
#         try:
#             instance = Components.objects.get(pk=pk)
#         except:
#             return Response({'error': 'Объекта с таким pk не существует'})
#
#         serializer = ComponentsSerializer(data=request.data, instance=instance)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'data': serializer.data})
#
#     def patch(self, request, *args,**kwargs):
#         pk = kwargs.get('pk', None)
#         if not pk:
#             return Response({'error': 'Метод patch не определён'})
#
#         try:
#             instance = Components.objects.get(pk=pk)
#         except:
#             return Response({'error': 'Объекта с таким pk не существует'})
#
#         serializer = ComponentsSerializer(data=request.data, instance=instance, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'data': serializer.data})
#
#     def delete(self, request, pk):
#
#         try:
#             instance = Components.objects.get(pk=pk)
#         except:
#             return Response({'error': 'Объекта с таким pk не существует'})
#
#         instance.delete()
#
#         return Response({'Сообщение': 'объект успешно удалён'})

# class ComponentsAPIList(generics.ListCreateAPIView):
#     queryset = Components.objects.all()
#     serializer_class = ComponentsSerializer
#
# class ComponentsAPIUpdate(generics.UpdateAPIView):
#     queryset = Components.objects.all()
#     serializer_class = ComponentsSerializer
#
# class ComponentsAPIDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Components.objects.all()
#     serializer_class = ComponentsSerializer

# class ComponentsViewSet(viewsets.ModelViewSet):
#     queryset = Components.objects.all()
#     serializer_class = ComponentsSerializer
#
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#
#     @action(methods=['get'],detail=True)
#     def category_detail(self, request, pk):
#         obj = Category.objects.get(pk=pk)
#         return Response({'cat': obj.c_name})
#
#     @action(methods=['get'], detail=False)
#     def category(self, request):
#         set = Category.objects.all()
#         return Response({'cats': [i.c_name for i in set]})
#
# class ComponentsAPIDestroy(generics.RetrieveDestroyAPIView):
#     queryset = Components.objects.all()
#     serializer_class = ComponentsSerializer
#
#     permission_classes = (IsAdminOrReadOnly,)
