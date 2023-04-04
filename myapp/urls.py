from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('register',views.register,name='register'),
     
    path('login_usage',views.login_usage,name='login_usage'),
    path('logout_page',views.logout_page,name='logout_page'),

    path('payment',views.payment,name='payment'),
    path('pay', views.pay, name='pay'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
  
      
    path('cart_page',views.cart_page,name="cart_page"),
    path('addtocart',views.add_to_cart,name="addtocart"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),

    path('fav_page',views.fav_page,name="fav_page"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),

    path('collections',views.collections,name='collections'),
    path('collections/<str:name>',views.collectionsview,name='collections'),
    path('collections/<str:cname>/<str:pname>',views.product_details,name='product_details'),

  
  
]