from django.shortcuts import render,redirect
import json
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt 
from django.http import HttpResponseBadRequest
from django.http import  JsonResponse
from .forms import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def home(request):
    products=Product.objects.filter(trending=1)
    return render(request, "store/index.html",{"products":products})

def payment(request):
    if request.user.is_authenticated:
      ordersummary=Mycart.objects.filter(user=request.user)
      return render(request,'store/payment.html',{"ordersummary":ordersummary})
    else:
      return redirect("home")
       

     
   

def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,'store/fav.html',{"fav":fav})
  else:
     return redirect("home")
 
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("favviewpage")
 
 
 
 
def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
    
def cart_page(request):
  if request.user.is_authenticated:
    cart=Mycart.objects.filter(user=request.user)
    return render(request,"store/cart.html",{"cart":cart})
  else:
  
    return redirect("home")

def remove_cart(request,cid):
  cartitem=Mycart.objects.get(id=cid)
  cartitem.delete()
  return redirect("cart_page")

def add_to_cart(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_qty=data['product_qty']
      product_id=data['pid']
      #print(request.user.id)
      product_status=Product.objects.get(id=product_id)
      if product_status:
        if Mycart.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:
            Mycart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)

def logout_page(request):
    if request.user.is_authenticated:
      logout(request)
      messages.success(request,"logout successfully")
    return render(request, "store/index.html")


def login_usage(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
      if request.method=="POST":    
         name=request.POST.get('username')
         pwd=request.POST.get('password')
         user=authenticate(request, username=name, password=pwd)
         if user is not None:
            login(request,user)
            messages.success(request,"login successfully")
            return redirect('home')
         else:
             messages.error(request,"Invalid username or password")
             return redirect('login_usage')
      return render(request,"store/login.html") 

      
def register(request):
    form=CustomUserForm()
    if request.method=="POST":
        form=CustomUserForm(request.POST)
        if form.is_valid():
          form.save()
          messages.success(request,"Registration Success you can login now..!")
          return redirect('login_usage')
    return render(request,"store/register.html",{"form":form})

def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request, "store/collections.html", {"catagory":catagory})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name,status=0)):
     products=Product.objects.filter(category__name=name)
     return render(request,"store/products/index.html",{"products":products,"category":name})
    else:
        messages.warning(request,"No Such Category Found")
        return redirect('collections')

def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"store/products/product_details.html",{"products":products})
        else:
            messages.error(request,"No Such Product Found")
            return redirect('collections')
    else:
        messages.error(request,"No Such Category Found")
        return redirect('collections')

def pay(request):
        currency = 'INR'
        amount = 20000  # Rs. 200
 
        # Create a Razorpay Order
        razorpay_order = client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
       # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
        context = {}
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
    
        return render(request, 'store/finalpayment.html', context=context)
    
 
# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt 
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:
 
                    # capture the payemt
                    client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()