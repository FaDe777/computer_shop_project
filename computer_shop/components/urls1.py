from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers

from .views import *

# router = routers.DefaultRouter()
# router.register(r'components',ComponentsViewSet)

profile_setting_patterns = [
    path('change_password/',ChangePassword.as_view(),name='change_pass'),
    path('change_email/',ChangeEmail.as_view(),name='change_email')
]

urlpatterns = [
    path('',home,name='home'),
    path('about/',about,name='about'),
    path('cart/',cart,name='cart'),
    path('cart/add/',cart_add_ajax,name='cart_add'),
    path('cart/del/',cart_del, name='cart_del'),
    path('cart/clear/',clear_cart,name='clear_cart'),
    path('login/',login,name='login'),
    path('register/',register,name='register'),
    path('confirm_email/',TemplateView.as_view(template_name='components/confirm_email.html'),name='confirm_email'),
    path('verify_email/<uidb64>/<token>/',EmailVerify.as_view(),name='email_verify'),
    path('logout/',logout_user,name='logout'),
    path('profile/<str:user>/',UserProfile.as_view(),name='user'),
    path('profile_settings/',ProfileSettings.as_view(),name='settings'),
    path('profile_settings/',include(profile_setting_patterns)),
    path('category/<slug:category_slug>/',list_components,name='components'),
    path('category/<slug:category_slug>/<slug:component_slug>/',show_component,name='component'),
    path('reply/',reply_ajax,name='reply_ajax'),
    path('reply_delete/',reply_delete_ajax,name='reply_delete_ajax'),
    path('comment/like/',comment_like,name='comment_like'),
    path('search/',search,name='search'),
    #path('category/<slug:category_slug>/<slug:component_slug>/reviews/',reviews,name='reviews'),
    path('ordering/',ordering,name='ordering'),
    path('order_success/',ordering,name='order_success'),
    path('check_order_status/',check_order_status,name='check_order_status'),
    path('order/<str:number>/<int:id>/',order_status,name='order_status'),
    # path('api/v1/',include(router.urls)),
    # path('api/v2/components/delete/<int:pk>/',ComponentsAPIDestroy.as_view()),
    path('notices/',notifications,name='notifications'),
    path('orders/',orders,name='orders'),
    path('orders/completed/',orders_completed,name='completed')

]


