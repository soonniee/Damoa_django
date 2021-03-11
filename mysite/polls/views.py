from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserDamoa,Product,WishList,AuctionHistory
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.core.paginator import Paginator
import logging
from .forms import *
import json
import requests
from datetime import datetime
from datetime import tzinfo,timedelta,datetime
from pytz import timezone
logger = logging.getLogger(__name__)
# Create your views here.
def oauth(request):
    code = request.GET['code']
    print('code='+str(code))
    app_rest_api_key = 'e02bad208c380c51c1fb527ccbea260f'
    redirect_uri = 'http://127.0.0.1:8000/polls/oauth'
    access_token_uri=f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={app_rest_api_key}&redirect_uri={redirect_uri}&code="+code
    access_token_data = requests.get(access_token_uri)
    
    json_data = access_token_data.json()
   
    access_token=json_data['access_token']
    user_profile_uri = "https://kapi.kakao.com/v2/user/me?access_token="
    user_profile_uri+=str(access_token)
    user_profile_info = requests.get(user_profile_uri)
    user_json = user_profile_info.json()
    
    user_nickname = user_json['properties']['nickname']
    user_email = user_json['kakao_account']['email']
    try:
        User.objects.create_user(username = user_nickname,email=user_email)
        return redirect('polls:home')
    except:
        return redirect('polls:home')
def kakao_login(request):
    app_rest_api_key = 'e02bad208c380c51c1fb527ccbea260f'
    redirect_uri = "http://127.0.0.1:8000/polls/oauth"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )
def kakao_callback(request):                                                                  
    params = urllib.parse.urlencode(request.GET)                                      
    return redirect(f'http://127.0.0.1:8000/account/login/kakao/callback?{params}')   
def signup(request):
    if request.method == "GET":
        return render(request, 'polls/signup_new.html')
    elif request.method == "POST":
        signup_name = request.POST['usrnm']
        try:
            signup_userid = request.POST['userid']
            signup_password = request.POST['password']
            signup_password_re = request.POST['password_re']
            signup_email = request.POST['email']

            data ={}
            if(len(signup_userid)==0 or len(signup_email)==0 or len(signup_password)==0 or len(signup_password_re)==0 or len(signup_name)==0):
                # print('aaaaaa')
                data['error']='Please input all!!'
                return render(request,'polls/signup_new.html',data)
            else:
                if not '@' in signup_email or not '.' in signup_email:
                    data['error']='Invalid Email Format!!'
                    return render(request,'polls/signup_new.html',data)
                else:
                    if(signup_password == signup_password_re):
                        User.objects.create_user(username = signup_userid,password = signup_password,email=signup_email)
                        
                        user = UserDamoa(user_name = signup_name, user_id =signup_userid, user_password = signup_password,email = signup_email,report_count=0)
                        user.save()
                        which = 'all'
                        return HttpResponseRedirect(reverse('polls:home',args=(which,)))
                    else:
                        data['error']='Password Incorrect!!'
                        return render(request,'polls/signup_new.html',data)
        except:
            data['error']='ID Already Exist!!'
            return render(request,'polls/signup_new.html',data)
def admin(request):
    userinfo = UserDamoa.objects.all()
    if request.method == "POST":
        del_user = UserDamoa.objects.get(pk=request.POST['deleteID'])
        User.objects.get(username=request.POST['deleteID']).delete()
        del_user.delete()
    return render(request,"polls/admin.html",{'userinfo':userinfo})
def admin_edit(request,user_id):
    admin_edit = UserDamoa.objects.get(pk=user_id)
    if request.method == "POST":
        if 'editID' in request.POST:
            user = UserDamoa.objects.get(pk=user_id)
            confirm_count = int(request.POST['confirm_count'])
            user.warning_count = confirm_count
            user.save()
            # userinfo = UserDamoa.objects.all()
            return HttpResponseRedirect(reverse('polls:admin'))
            # return render(request,"polls/admin.html",{'userinfo':userinfo})
    return render(request,"polls/admin_edit.html",{'userinfo':admin_edit})
def admin_report(request,reported_id):
    reported = Report.objects.filter(seller=reported_id)
     
    list=[]
    for i in reported:
        list.append(i.prod_id_id)
    reported_product = Product.objects.filter(prod_id__in=list)
    
    return render(request,'polls/admin_report.html',{'reported':reported,'my_product':reported_product,'reported_user':reported_id})
def admin_reply(request,report_id):
    reported = Report.objects.get(id=report_id)
    reply_product = Product.objects.get(pk=reported.prod_id_id)
    if request.method == 'POST':
        reply = Report.objects.get(id=report_id)
        reply_content= request.POST['reply_content']
        reply.reply = 1
        reply.reply_content =reply_content
        reply.save()
        return HttpResponseRedirect(reverse('polls:admin_report',args=(reported.seller,)))
    else:
        return render(request,'polls/admin_reply.html',{'reported':reported,'my_product':reply_product})
def admin_userinfo_sales(request,user_id):
    sales_prod = Product.objects.filter(seller=user_id)
    return render(request,'polls/admin_userinfo_sales.html',{'sales_prod':sales_prod,'id':user_id})
def admin_userinfo_purchase(request,user_id):
    user_purchase = ShoppingList.objects.filter(user_id_id=user_id)
    list=[]
    for i in user_purchase:
        list.append(i.prod_id_id)
    purchase_prod = Product.objects.filter(prod_id__in=list) 
    return render(request,'polls/admin_userinfo_purchase.html',{'purchase_prod':purchase_prod,'id':user_id})
def login(request):

    if request.method == "GET":
        return render(request, 'polls/login_new.html')
    elif request.method == "POST":
        login_userid = request.POST['userid']
        login_password = request.POST['password']
        if(login_userid == "admin" and login_password == "admin!!"):
            return HttpResponseRedirect(reverse('polls:admin'))
        else:
            user = auth.authenticate(request, username=login_userid, password = login_password)
            
            if user is None:
                return render(request, 'polls/login_new.html',{'error': 'ID or Password incorrect!!'})
            else:
                # user = User.objects.get(user_id =login_userid)
                # if check_password(login_password, user.user_password):
                #     request.session['user'] = user.user_id
                    key = UserDamoa.objects.get(pk=login_userid)
                    auth.login(request,user)
                    # return HttpResponseRedirect(reverse('polls:index'))
                    # return render(request,'polls/index.html',{'id':login_userid})
                    which='all'
                    return HttpResponseRedirect(reverse('polls:home',args=(which,)))
def mypage_seller(request):
    userdamoa_id = request.user.username
    auction_history = AuctionHistory.objects.all()
    if request.method == "POST":
        if 'edit' in request.POST:
            prod_id = request.POST['edit']
            return HttpResponseRedirect(reverse('polls:mypage_seller_edit', args=(prod_id,)))

        if 'deleteProd' in request.POST:
            
            del_prod = Product.objects.get(pk=request.POST['deleteProd'])
            del_prod.delete()
            
        my_product = Product.objects.all()
        
        return render(request,'polls/mypage_seller.html',{'id': userdamoa_id,'my_product': my_product})
    else: 
        my_product = Product.objects.all()
        return render(request,'polls/mypage_seller.html',{'id': userdamoa_id,'my_product': my_product,'auction_history':auction_history})
def mypage_seller_edit(request,prod_id):
    userdamoa_id = request.user.username
    my_product = Product.objects.get(pk=prod_id)
    if request.method =='POST':
        auction = AuctionHistory.objects.filter(prod_id_id=prod_id)
        auction.delete()
        edit_prod = Product.objects.get(pk=prod_id)
        edit_prod.prod_name = request.POST['name']
        edit_prod.place = request.POST['place']
        edit_prod.bid_unit = int(request.POST['bid_unit'])
        edit_prod.bid_start = request.POST['start']
        edit_prod.bid_end = request.POST['end']
            # print(edit_prod.start_date)
        if(request.POST['now']=="possible"):
            edit_prod.now_price = int(request.POST['now_price'])
            edit_prod.now = 0
        else : edit_prod.now = 1
        edit_prod.phone = request.POST['phone']
        edit_prod.price = int(request.POST['price'])
        edit_prod.current_price = int(request.POST['price'])
        edit_prod.category = request.POST['category']
        edit_prod.img = request.FILES['img']
        edit_prod.likey = 0
        edit_prod.save()
        return HttpResponseRedirect(reverse('polls:mypage_seller'))
    else :
        return render(request,'polls/mypage_seller_edit.html',{'id': userdamoa_id,'my_product': my_product})
def report(request,which,prod_id):
    userdamoa_id = request.user.username
    user = UserDamoa.objects.get(pk=userdamoa_id)
    my_product = Product.objects.get(pk=prod_id)
    if request.method=="POST":
        user_reported = UserDamoa.objects.get(pk=my_product.user_id_id)
        user_reported.report_count+=1
        user_reported.save()
        report_title = request.POST['report_title']
        report_content = request.POST['report_content']
        report = Report()
        report.seller = my_product.user_id_id
        report.prod_name = my_product.prod_name
        report.user_id_id = userdamoa_id
        report.prod_id_id = prod_id
        report.title = report_title
        report.content = report_content
        report.save()
        return HttpResponseRedirect(reverse('polls:home',args=(which,)))
    else:
        # report_product = request.POST['report_product']
        return render(request,'polls/report.html',{'id': userdamoa_id,'my_product': my_product,'user':user})


def mypage_wish(request):
    auction_history = AuctionHistory.objects.all()
    userdamoa_id = request.user.username
    wish = WishList.objects.filter(user_id_id=userdamoa_id)
    list=[]
    for i in wish:
        list.append(i.prod_id_id)
    wish_product= Product.objects.filter(prod_id__in=list)
    if request.method=='POST':
        if 'bidding' in request.POST:
            print('bidding')
            prod_id = request.POST['bidding']
            which = 'all'
            return HttpResponseRedirect(reverse('polls:bidding', args=(which,prod_id,)))
        if 'buy_now' in request.POST:
            now_end = datetime.now(timezone('UTC'))
            now_end = now_end.astimezone(timezone('Asia/Seoul'))
            
            prod_id = request.POST['buy_now']
            product = Product.objects.get(pk=prod_id)
            product.sold = 1
            product.now_sold=1
            product.current_price = product.now_price
            product.now_buyer = userdamoa_id
            product.now_end = now_end
            product.save()
            wish_product= Product.objects.filter(prod_id__in=list)
            # product.save()
            shopping = ShoppingList()
            shopping.prod_id_id = prod_id
            shopping.user_id_id = userdamoa_id
            shopping.save()
            return render(request,'polls/mypage_wishlist.html',{'id': userdamoa_id,'my_product':wish_product,'auction_history':auction_history})
    else:
        return render(request,'polls/mypage_wishlist.html',{'id': userdamoa_id,'my_product': wish_product,'auction_history':auction_history})
def mypage_shopping(request):
    auction_history = AuctionHistory.objects.all()
    userdamoa_id = request.user.username
    shopping = ShoppingList.objects.filter(user_id_id=userdamoa_id)
    list=[]
    for i in shopping:
        list.append(i.prod_id_id)
     
    shopping_product= Product.objects.filter(prod_id__in=list)
    
    return render(request,'polls/mypage_shopping.html',{'id': userdamoa_id,'my_product': shopping_product,'auction_history':auction_history})
def mypage_report(request):
    userdamoa_id = request.user.username
    report = Report.objects.filter(user_id_id = userdamoa_id)
    list=[]
    for i in report:
        list.append(i.prod_id_id)
    reported_product = Product.objects.filter(prod_id__in=list)
    return render(request,'polls/mypage_report.html',{'id': userdamoa_id,'report':report,'my_product':reported_product})
def mypage_inquiry_buying(request):
    userdamoa_id = request.user.username
    inquiry = Inquiry.objects.filter(user_id_id = userdamoa_id)
    list=[]
    for i in inquiry:
        list.append(i.prod_id_id)
    inquiry_product = Product.objects.filter(prod_id__in=list)
    return render(request,'polls/mypage_inquiry_buying.html',{'id': userdamoa_id,'inquiry':inquiry,'my_product':inquiry_product})
def mypage_inquiry_selling(request):
    userdamoa_id = request.user.username
    inquiry = Inquiry.objects.filter(seller = userdamoa_id)
    list=[]
    for i in inquiry:
        list.append(i.prod_id_id)
    inquiry_product = Product.objects.filter(prod_id__in=list)
    if request.method == 'POST':
        inquiry_id = request.POST['reply_inquiry']
        inquiry_reply = Inquiry.objects.get(pk=inquiry_id)
        inquiry_reply.reply_content = request.POST['reply_content']
        inquiry_reply.reply = 1
        inquiry_reply.save()
        return HttpResponseRedirect(reverse('polls:mypage_inquiry_selling'))
    else:
        return render(request,'polls/mypage_inquiry_selling.html',{'id': userdamoa_id,'inquiry':inquiry,'my_product':inquiry_product})
def mypage_cart(request):
    auction_history = AuctionHistory.objects.all()
    userdamoa_id = request.user.username
    cart = Cart.objects.filter(user_id_id=userdamoa_id)
    list=[]
    for i in cart:
        list.append(i.prod_id_id)
     
    cart_product= Product.objects.filter(prod_id__in=list)
    if request.method=="POST":
        
        if 'remove_selected' in request.POST:
            
            remove_list = request.POST.getlist('checkbox')
            

            if len(remove_list)==0:
                
                return render(request,'polls/mypage_cart.html',{'id': userdamoa_id,'my_product':cart_product,'auction_history':auction_history,'error':'More than One should be Selected!!'})
            else:
                for i in remove_list:
                    remove_cart = Cart.objects.get(prod_id_id=i,user_id_id = userdamoa_id)
                    remove_cart.delete()
                return HttpResponseRedirect(reverse('polls:mypage_cart'))
        if 'bidding' in request.POST:
            
            prod_id = request.POST['bidding']
            which='all'
            return HttpResponseRedirect(reverse('polls:bidding', args=(which,prod_id,)))
        if 'buy_selected' in request.POST:
            buy_list = request.POST.getlist('checkbox')
            
            if len(buy_list)==0:
                return render(request,'polls/mypage_cart.html',{'id': userdamoa_id,'my_product':cart_product,'auction_history':auction_history,'error':'More than One should be Selected!!'})
            else:
                buy_product = Product.objects.filter(prod_id__in=buy_list)

                now_end = datetime.now(timezone('UTC'))
                now_end = now_end.astimezone(timezone('Asia/Seoul'))
                for product in buy_product:
                    product.sold = 1
                    product.now_sold=1
                    product.now_buyer = userdamoa_id
                    product.now_end = now_end
                    product.save()

                    shopping = ShoppingList()
                    shopping.prod_id_id = product.prod_id
                    shopping.user_id_id = userdamoa_id
                    shopping.save()
                for i in buy_list:
                    remove_cart = Cart.objects.get(prod_id_id=i,user_id_id = userdamoa_id)
                    remove_cart.delete()
                return HttpResponseRedirect(reverse('polls:mypage_cart'))
        if 'pk' in request.POST:
            
            total = 0
            cart = Cart.objects.all()
            for i in cart:
                if i.check == 1:
                    total = total + i.now_price
            pk = request.POST.get('pk',None)
            cart_pk = Cart.objects.get(prod_id_id=pk,user_id_id=userdamoa_id)
            if cart_pk.check == 1:
                cart_pk.check = 0
                cart_pk.save() 
                total = total - cart_pk.now_price
            else:
                cart_pk.check = 1
                cart_pk.save()
                total = total + cart_pk.now_price
            
            context = {'total':total}
            return HttpResponse(json.dumps(context),content_type="application/json")
    else:
        return render(request,'polls/mypage_cart.html',{'id': userdamoa_id,'my_product': cart_product,'auction_history':auction_history})
def index(request,which):
    auth.logout(request)
    if which=='all':
        now = datetime.now(timezone('UTC'))
        now = now.astimezone(timezone('Asia/Seoul'))
        
        prod = Product.objects.all()
        for i in prod:
            if i.bid_end < now:
                i.sold = 1
            i.save()
        prod = Product.objects.all().order_by('-bid_start')
        filter_display='Latest'
        if request.method =='POST':
            prod_filter = Product.objects.all().order_by('-bid_start')
            
            if 'hot' in request.POST:
                filter_display='Hot'
                category=request.POST['hot']
                prod_filter = Product.objects.all().order_by('-likey')
                return render(request,'polls/index.html', {'prod':prod_filter,'category':category,'filter_display':filter_display})
            elif 'latest' in request.POST:
                filter_display='Latest'
                category=request.POST['latest']
                prod_filter = Product.objects.all().order_by('-bid_start')
                return render(request,'polls/index.html', {'prod':prod_filter,'category':category,'filter_display':filter_display})
            elif 'last' in request.POST:
                filter_display='Last Minute'
                category=request.POST['last']
                prod_filter = Product.objects.all().order_by('bid_end')
                return render(request,'polls/index.html', {'prod':prod_filter,'category':category,'filter_display':filter_display})
            if 'All' in request.POST:
                prod_category = prod_filter.all()
                return render(request,'polls/index.html', {'prod':prod_category,'category':'All','filter_display':filter_display})
            if 'IT' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['IT'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'IT','filter_display':filter_display})
            if 'Clothes' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Clothes'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Clothes','filter_display':filter_display})
            if 'Shoes' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Shoes'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Shoes','filter_display':filter_display})
            if 'Books' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Books'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Books','filter_display':filter_display})
            if 'Furniture' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Furniture'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Furniture','filter_display':filter_display})
            if 'Etc' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Etc'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Etc','filter_display':filter_display})
            if 'search' in request.POST:
                category = request.POST['search']
                if 'seller_search' in request.POST:
                    seller_search = request.POST['seller_search']
                    
                else :
                    seller_search =""
                if 'product_search' in request.POST:
                    product_search = request.POST['product_search']
                    
                else :
                    product_search =""
                if 'price_search' in request.POST:
                    
                    price_search=[]
                    if int(request.POST['price_search'])==1:
                        price_search.append(0)
                        price_search.append(50)
                    if int(request.POST['price_search'])==2:
                        price_search.append(50)
                        price_search.append(100)
                    if int(request.POST['price_search'])==3:
                        price_search.append(100)
                        price_search.append(500)
                    if int(request.POST['price_search'])==4:
                        price_search.append(500)
                        price_search.append(1000)
                    if int(request.POST['price_search'])==5:
                        price_search.append(1000)
                        price_search.append(5000)
                    if int(request.POST['price_search'])==6:
                        price_search.append(5000)
                        price_search.append(10000000)
                    
                    
                else :
                    price_search =""
                if len(seller_search) == 0 and len(price_search)==0 and len(product_search)==0:
                    data={}
                    data['error']='Input Search Keyword!!'
                    return render(request,'polls/index.html', {'prod':prod_filter,'error':'Input Search Keyword!!','category':'All','filter_display':filter_display})
                else:
                    if category =='All':
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])) & Q(seller = seller_search))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})
                    else :
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search)& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1])) & Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(price__range=(price_search[0],price_search[1]))& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search)& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

            

            if 'pk' in request.POST:

                
                return HttpResponseRedirect(reverse('polls:login_new'))
            if 'bidding' in request.POST:
                
                return HttpResponseRedirect(reverse('polls:login_new'))
            if 'buy_now' in request.POST:
                return HttpResponseRedirect(reverse('polls:login_new'))
            if 'add_cart' in request.POST:
                return HttpResponseRedirect(reverse('polls:login_new'))
        else:
            return render(request,'polls/index.html',{'prod':prod,'category':'All'})
    elif which=='auction':
        now = datetime.now(timezone('UTC'))
        now = now.astimezone(timezone('Asia/Seoul'))
        
        prod = Product.objects.filter(now=1)
        for i in prod:
            if i.bid_end < now:
                i.sold = 1
            i.save()
        prod = Product.objects.filter(now=1).order_by('-bid_start')
        filter_display='Latest'
        if request.method =='POST':
            prod_filter = Product.objects.filter(now=1).order_by('-bid_start')
            
            if 'hot' in request.POST:
                filter_display='Hot'
                category=request.POST['hot']
                prod_filter = Product.objects.filter(now=1).order_by('-likey')
                return render(request,'polls/index.html', {'prod':prod_filter,'category':category,'filter_display':filter_display})
            elif 'latest' in request.POST:
                filter_display='Latest'
                category=request.POST['latest']
                prod_filter = Product.objects.filter(now=1).order_by('-bid_start')
                return render(request,'polls/index.html', {'prod':prod_filter,'category':category,'filter_display':filter_display})
            elif 'last' in request.POST:
                filter_display='Last Minute'
                category=request.POST['last']
                prod_filter = Product.objects.filter(now=1).order_by('bid_end')
                return render(request,'polls/index.html', {'prod':prod_filter,'category':category,'filter_display':filter_display})
            if 'All' in request.POST:
                prod_category = prod_filter.filter(now=1)
                return render(request,'polls/index.html', {'prod':prod_category,'category':'All','filter_display':filter_display})
            if 'IT' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['IT'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'IT','filter_display':filter_display})
            if 'Clothes' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Clothes'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Clothes','filter_display':filter_display})
            if 'Shoes' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Shoes'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Shoes','filter_display':filter_display})
            if 'Books' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Books'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Books','filter_display':filter_display})
            if 'Furniture' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Furniture'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Furniture','filter_display':filter_display})
            if 'Etc' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Etc'])
                return render(request,'polls/index.html', {'prod':prod_category,'category':'Etc','filter_display':filter_display})
            if 'search' in request.POST:
                category = request.POST['search']
                if 'seller_search' in request.POST:
                    seller_search = request.POST['seller_search']
                    
                else :
                    seller_search =""
                if 'product_search' in request.POST:
                    product_search = request.POST['product_search']
                    
                else :
                    product_search =""
                if 'price_search' in request.POST:
                    
                    price_search=[]
                    if int(request.POST['price_search'])==1:
                        price_search.append(0)
                        price_search.append(50)
                    if int(request.POST['price_search'])==2:
                        price_search.append(50)
                        price_search.append(100)
                    if int(request.POST['price_search'])==3:
                        price_search.append(100)
                        price_search.append(500)
                    if int(request.POST['price_search'])==4:
                        price_search.append(500)
                        price_search.append(1000)
                    if int(request.POST['price_search'])==5:
                        price_search.append(1000)
                        price_search.append(5000)
                    if int(request.POST['price_search'])==6:
                        price_search.append(5000)
                        price_search.append(10000000)
                    
                    
                else :
                    price_search =""
                if len(seller_search) == 0 and len(price_search)==0 and len(product_search)==0:
                    data={}
                    data['error']='Input Search Keyword!!'
                    return render(request,'polls/index.html', {'prod':prod_filter,'error':'Input Search Keyword!!','category':'All','filter_display':filter_display})
                else:
                    if category =='All':
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1]))&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})
                    else :
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1]))& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/index.html', {'prod':result,'category':category,'filter_display':filter_display})

            

            if 'pk' in request.POST:

                
                return HttpResponseRedirect(reverse('polls:login_new'))
            if 'bidding' in request.POST:
                
                return HttpResponseRedirect(reverse('polls:login_new'))
            if 'buy_now' in request.POST:
                return HttpResponseRedirect(reverse('polls:login_new'))
            if 'add_cart' in request.POST:
                return HttpResponseRedirect(reverse('polls:login_new'))
        else:
            return render(request,'polls/index.html',{'prod':prod,'category':'All','filter_display':filter_display})

def home(request,which):
    if which == 'all':

    ######realtime soldout display -> 다른 페이지에도 적용??
        now = datetime.now(timezone('UTC'))
        now = now.astimezone(timezone('Asia/Seoul'))
        
        prod = Product.objects.all()
        for i in prod:
            if i.bid_end < now:
                i.sold = 1
            i.save()
        prod = Product.objects.all().order_by('-bid_start')
        
        ######realtime soldout display -> 다른 페이지에도 적용??
        
        userdamoa_id = request.user.username
        
        user_wish = WishList.objects.filter(user_id_id = userdamoa_id)
        prod_list=[]
        filter_display='Latest'
        for i in user_wish:
            prod_list.append(i.prod_id_id)
        if request.method =='POST':
            prod_filter = Product.objects.all().order_by('-bid_start')
            
            if 'hot' in request.POST:
                print('aaa')
                filter_display='Hot'
                category=request.POST['hot']
                prod_filter = Product.objects.all().order_by('-likey')
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'category':category,'which':which,'filter_display':filter_display})
            elif 'latest' in request.POST:
                filter_display='Latest'
                category=request.POST['latest']
                prod_filter = Product.objects.all().order_by('-bid_start')
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'category':category,'which':which,'filter_display':filter_display})
            elif 'last' in request.POST:
                filter_display='Last Minute'
                category=request.POST['last']
                prod_filter = Product.objects.all().order_by('bid_end')
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'category':category,'which':which,'filter_display':filter_display})
            # else :
            #     prod_filter = Product.objects.all().order_by('-bid_end')
                
            if 'All' in request.POST:
                prod_category = prod_filter
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'All','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'IT' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['IT'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'IT','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Clothes' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Clothes'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Clothes','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Shoes' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Shoes'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Shoes','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Books' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Books'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Books','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Furniture' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Furniture'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Furniture','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Etc' in request.POST:
                prod_category = prod_filter.filter(category = request.POST['Etc'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Etc','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'search' in request.POST:
                category = request.POST['search']
                if 'seller_search' in request.POST:
                    seller_search = request.POST['seller_search']
                    
                else :
                    seller_search =""
                if 'product_search' in request.POST:
                    product_search = request.POST['product_search']
                    
                else :
                    product_search =""
                if 'price_search' in request.POST:
                    
                    price_search=[]
                    if int(request.POST['price_search'])==1:
                        price_search.append(0)
                        price_search.append(50)
                    if int(request.POST['price_search'])==2:
                        price_search.append(50)
                        price_search.append(100)
                    if int(request.POST['price_search'])==3:
                        price_search.append(100)
                        price_search.append(500)
                    if int(request.POST['price_search'])==4:
                        price_search.append(500)
                        price_search.append(1000)
                    if int(request.POST['price_search'])==5:
                        price_search.append(1000)
                        price_search.append(5000)
                    if int(request.POST['price_search'])==6:
                        price_search.append(5000)
                        price_search.append(10000000)
                    
                    
                else :
                    price_search =""
                if len(seller_search) == 0 and len(price_search)==0 and len(product_search)==0:
                    data={}
                    data['error']='Input Search Keyword!!'
                    return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'error':'Input Search Keyword!!','category':'All','prod_list':prod_list,'which':which,'filter_display':filter_display})
                else:
                    if category =='All':
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(seller = seller_search))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})
                    else :
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search)& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1]))& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search)& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search)& Q(category=category))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

            

            if 'pk' in request.POST:

                like_chk = 0
                pk = request.POST.get('pk',None)
                
                prod_pk = Product.objects.get(pk=pk)
                
                
                if WishList.objects.filter(user_id_id=userdamoa_id,prod_id_id=pk).exists():
                    
                    del_wish = WishList.objects.filter(user_id_id=userdamoa_id,prod_id_id=pk)
                    del_wish.delete()
                    prod_pk.likey -=1
                    prod_pk.save()
                else:
                    
                    wish = WishList(user_id_id=userdamoa_id,prod_id_id =pk)
                    wish.save()
                    prod_pk.likey +=1
                    prod_pk.save()
                    like_chk=1
                prod = Product.objects.get(pk=pk)
                context = {'likes_count':prod.likey,'like':like_chk}
                return HttpResponse(json.dumps(context),content_type="application/json")
            if 'bidding' in request.POST:
                
                prod_id = request.POST['bidding']

                return HttpResponseRedirect(reverse('polls:bidding', args=(which,prod_id,)))
            if 'buy_now' in request.POST:
                now_end = datetime.now(timezone('UTC'))
                now_end = now_end.astimezone(timezone('Asia/Seoul'))
                
                prod_id = request.POST['buy_now']
                product = Product.objects.get(pk=prod_id)
                product.sold = 1
                product.now_sold=1
                product.current_price = product.now_price
                product.now_buyer = userdamoa_id
                product.now_end = now_end
                product.save()
                prod = prod_filter.all()
                # product.save()
                shopping = ShoppingList()
                shopping.prod_id_id = prod_id
                shopping.user_id_id = userdamoa_id
                shopping.save()
                return render(request,'polls/home.html',{'id': userdamoa_id,'prod':prod,'prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'add_cart' in request.POST:
                cart_prod = Product.objects.get(pk=request.POST['add_cart'])
                cart = Cart()
                cart.user_id_id = userdamoa_id
                cart.prod_id_id = request.POST['add_cart']
                cart.now_price = cart_prod.now_price
                cart.save()
                return render(request,'polls/home.html',{'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'which':which,'filter_display':filter_display})
        else: 
            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod,'prod_list':prod_list,'category':'All','which':which,'filter_display':filter_display})
    elif which =='auction':
        now = datetime.now(timezone('UTC'))
        now = now.astimezone(timezone('Asia/Seoul'))
        
        prod = Product.objects.filter(now=1)
        for i in prod:
            if i.bid_end < now:
                i.sold = 1
            i.save()
        prod = Product.objects.filter(now=1).order_by('-bid_start')
        ######realtime soldout display -> 다른 페이지에도 적용??
        filter_display='Latest'
        userdamoa_id = request.user.username
        user_wish = WishList.objects.filter(user_id_id = userdamoa_id)
        prod_list=[]
        for i in user_wish:
            prod_list.append(i.prod_id_id)
        if request.method =='POST':
            prod_filter = Product.objects.filter(now=1).order_by('-bid_start')
            if 'hot' in request.POST:
                filter_display='Hot'
                category=request.POST['hot']
                prod_filter = Product.objects.filter(now=1).order_by('-likey')
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'category':category,'which':which,'filter_display':filter_display})
            elif 'latest' in request.POST:
                filter_display='Latest'
                category=request.POST['latest']
                prod_filter = Product.objects.filter(now=1).order_by('-bid_start')
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'category':category,'which':which,'filter_display':filter_display})
            elif 'last' in request.POST:
                filter_display='Last Minute'
                category=request.POST['last']
                prod_filter = Product.objects.filter(now=1).order_by('bid_end')
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'prod_list':prod_list,'category':category,'which':which,'filter_display':filter_display})
            if 'All' in request.POST:
                prod_category = prod_filter.filter(now=1)
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'All','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'IT' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['IT'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'IT','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Clothes' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Clothes'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Clothes','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Shoes' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Shoes'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Shoes','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Books' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Books'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Books','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Furniture' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Furniture'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Furniture','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'Etc' in request.POST:
                prod_category = prod_filter.filter(now=1,category = request.POST['Etc'])
                return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_category,'category':'Etc','prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'search' in request.POST:
                category = request.POST['search']
                if 'seller_search' in request.POST:
                    seller_search = request.POST['seller_search']
                    
                else :
                    seller_search =""
                if 'product_search' in request.POST:
                    product_search = request.POST['product_search']
                    
                else :
                    product_search =""
                if 'price_search' in request.POST:
                    
                    price_search=[]
                    if int(request.POST['price_search'])==1:
                        price_search.append(0)
                        price_search.append(50)
                    if int(request.POST['price_search'])==2:
                        price_search.append(50)
                        price_search.append(100)
                    if int(request.POST['price_search'])==3:
                        price_search.append(100)
                        price_search.append(500)
                    if int(request.POST['price_search'])==4:
                        price_search.append(500)
                        price_search.append(1000)
                    if int(request.POST['price_search'])==5:
                        price_search.append(1000)
                        price_search.append(5000)
                    if int(request.POST['price_search'])==6:
                        price_search.append(5000)
                        price_search.append(10000000)
                    
                    
                else :
                    price_search =""
                if len(seller_search) == 0 and len(price_search)==0 and len(product_search)==0:
                    data={}
                    data['error']='Input Search Keyword!!'
                    return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod_filter,'error':'Input Search Keyword!!','category':'All','prod_list':prod_list,'which':which,'filter_display':filter_display})
                else:
                    if category =='All':
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search) &Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1]))&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})
                    else :
                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(prod_name__icontains=product_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1])) & Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)!=0 and len(product_search)==0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(current_price__range=(price_search[0],price_search[1]))& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search) & Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)!=0 and len(seller_search)==0:
                            result = prod_filter.filter(Q(prod_name__icontains=product_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

                        if len(price_search)==0 and len(product_search)==0 and len(seller_search)!=0:
                            result = prod_filter.filter(Q(seller = seller_search)& Q(category=category)&Q(now=1))
                            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':result,'category':category,'prod_list':prod_list,'which':which,'filter_display':filter_display})

            

            if 'pk' in request.POST:

                like_chk = 0
                pk = request.POST.get('pk',None)
                
                prod_pk = Product.objects.get(pk=pk)
                
                
                if WishList.objects.filter(user_id_id=userdamoa_id,prod_id_id=pk).exists():
                    
                    del_wish = WishList.objects.filter(user_id_id=userdamoa_id,prod_id_id=pk)
                    del_wish.delete()
                    prod_pk.likey -=1
                    prod_pk.save()
                else:
                    
                    wish = WishList(user_id_id=userdamoa_id,prod_id_id =pk)
                    wish.save()
                    prod_pk.likey +=1
                    prod_pk.save()
                    like_chk=1
                prod = Product.objects.get(pk=pk)
                context = {'likes_count':prod.likey,'like':like_chk}
                return HttpResponse(json.dumps(context),content_type="application/json")
            if 'bidding' in request.POST:
                
                prod_id = request.POST['bidding']
                return HttpResponseRedirect(reverse('polls:bidding', args=(which,prod_id,)))
            if 'buy_now' in request.POST:
                now_end = datetime.now(timezone('UTC'))
                now_end = now_end.astimezone(timezone('Asia/Seoul'))
                
                prod_id = request.POST['buy_now']
                product = Product.objects.get(pk=prod_id)
                product.sold = 1
                product.now_sold=1
                product.current_price = product.now_price
                product.now_buyer = userdamoa_id
                product.now_end = now_end
                product.save()
                prod =prod_filter.all()
                # product.save()
                shopping = ShoppingList()
                shopping.prod_id_id = prod_id
                shopping.user_id_id = userdamoa_id
                shopping.save()
                return render(request,'polls/home.html',{'id': userdamoa_id,'prod':prod,'prod_list':prod_list,'which':which,'filter_display':filter_display})
            if 'add_cart' in request.POST:
                
                cart = Cart()
                cart.user_id_id = userdamoa_id
                cart.prod_id_id = request.POST['add_cart']
                cart.save()
                return render(request,'polls/home.html',{'id': userdamoa_id,'prod':prod,'prod_list':prod_list,'which':which,'filter_display':filter_display})
        else: 
            return render(request,'polls/home.html', {'id': userdamoa_id,'prod':prod,'prod_list':prod_list,'category':'All','which':which,'filter_display':filter_display})

# def auction(request):
#     return HttpResponseRedirect(reverse('polls:home'))   
def bidding(request,which,prod_id):
    now = datetime.now(timezone('UTC'))
    now = now.astimezone(timezone('Asia/Seoul'))
    auction_history = AuctionHistory.objects.all()
    userdamoa_id = request.user.username
    user = UserDamoa.objects.get(pk = userdamoa_id)
    my_product = Product.objects.get(pk=prod_id)
    if my_product.bid_end < now:
        my_product.sold=1
    my_product.save()
    # print(my_product.bid_end)
    # print(my_product.bid_end.astimezone(timezone('Asia/Seoul')))
    end_time = my_product.bid_end.astimezone(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
    max = my_product.current_price
    
    
    # auction_his = AuctionHistory.objects.filter(prod_id = prod_id)
    
    if request.method == 'POST':
        auction_his = AuctionHistory()
        auction_his.prod_id_id = my_product.prod_id
        auction_his.bid_id_id = user.user_id
        auction_his.bid_price = request.POST['bid_price']
        auction_his.save()
        my_product.current_price = request.POST['bid_price']
        my_product.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # return HttpResponseRedirect(reverse('polls:home',args=(which,)))
    else:
        top_bid = AuctionHistory.objects.filter(prod_id_id=prod_id,bid_price = max)
        if top_bid.exists():
            top_bid = AuctionHistory.objects.get(prod_id_id=prod_id,bid_price = max)
            top_bidder = top_bid.bid_id_id
            bidding_price = max + my_product.bid_unit
            return render(request,'polls/bidding.html', {'id': userdamoa_id,'my_product':my_product,'current_price':max,'top_bidder':top_bidder,'bidding_price':bidding_price,'auction_history':auction_history,'end_time':end_time})
        else:
            top_bidder = 'You are the First Bidder'
            bidding_price = max + my_product.bid_unit
            return render(request,'polls/bidding.html', {'id': userdamoa_id,'my_product':my_product,'current_price':max,'top_bidder':top_bidder,'bidding_price':bidding_price,'auction_history':auction_history,'end_time':end_time})
def counsel(request,which,prod_id):
    userdamoa_id = request.user.username
    user = UserDamoa.objects.get(pk = userdamoa_id)
    my_product = Product.objects.get(pk=prod_id)
    if request.method=='POST':
        inquiry = Inquiry()
        inquiry.seller = my_product.seller
        inquiry.user_id_id = userdamoa_id
        inquiry.prod_id_id = prod_id
        inquiry.prod_name = my_product.prod_name
        inquiry.title = request.POST['inquiry_title']
        inquiry.content = request.POST['inquiry_content']
        inquiry.save()
        return HttpResponseRedirect(reverse('polls:home',args=(which,)))
    return render(request,'polls/counsel.html',{'id':userdamoa_id,'my_product':my_product})
def register(request):
    if not request.user.is_authenticated:
        which = 'all'
        return HttpResponseRedirect(reverse('polls:login_new'))
    else:
        userdamoa_id = request.user.username
        
        user = UserDamoa.objects.get(pk = userdamoa_id)
        if request.method == "POST":
            if len(request.POST['name'])==0 or len(request.POST['place'])==0 or len(request.POST['bid_unit'])==0 or len(request.POST['start'])==0 or len(request.POST['end'])==0 or len(request.POST['now'])==0 or len(request.POST['name'])==0 or len(request.POST['phone'])==0 or len(request.POST['price'])==0 or len(request.POST['category'])==0 or 'img' in request.POST or (request.POST['now']=='possible' and len(request.POST['now_price'])==0):
                data ={}
                data['error']='Please input all!!'
                return render(request,'polls/register_product.html',{'id': userdamoa_id,'error':'Please input all!!'})
            else:
                prod = Product()
                prod.user_id_id = user.user_id
                prod.seller = user.user_id
                prod.prod_name = request.POST['name']
                prod.place = request.POST['place']
                prod.bid_unit = int(request.POST['bid_unit'])
                start = request.POST['start'].replace('T',' ')
                end =  request.POST['end'].replace('T',' ')
                start = datetime.strptime(start,'%Y-%m-%d %H:%M')
            
                start = start.astimezone(timezone('Asia/Seoul'))
                end = datetime.strptime(end,'%Y-%m-%d %H:%M')
                
                end = end.astimezone(timezone('Asia/Seoul'))
            
                prod.bid_start = start
                prod.bid_end = end
                
                if(request.POST['now']=="possible"):
                    prod.now_price = int(request.POST['now_price'])
                    prod.now = 0
                else : prod.now = 1
                prod.phone = request.POST['phone']
                prod.price = int(request.POST['price'])
                prod.current_price = int(request.POST['price'])
                prod.category = request.POST['category']
                prod.img = request.FILES['img']
                prod.save()
                which ='all'
                return HttpResponseRedirect(reverse('polls:mypage_seller'))
            
        else:
            return render(request,'polls/register_product.html',{'id': userdamoa_id})
# def allcontent(request,userskku_id):
#     user = UserSKKU.objects.get(pk = userskku_id)
#
#     eval = Evaluation.objects.all()
#
#     course = Course.objects.all()
#
#     score = Score.objects.all()
#
#     recom = Recommend.objects.all()
#     paginator = Paginator(course,3)
#     page=request.GET.get('page')
#     posts= paginator.get_page(page)
#     if 'likeyID' in request.POST:
#         recom_count = Recommend.objects.get(pk = request.POST['likeyID'])
#         recom_count.recom_num = recom_count.recom_num + 1
#         recom_count.save()
#     if 'searchID' in request.POST:
#         course_search = Course.objects.filter(course_name__contains=request.POST['searchID'])
#         paginator_search = Paginator(course_search,3)
#         page_search=request.GET.get('page')
#         posts_search= paginator_search.get_page(page_search)
#         return render(request,'polls/search.html', {'userid': user,'eval':eval,'course':course_search,'score':score,'recom':recom,'query':request.POST['searchID'],'posts':posts_search})
#     return render(request,'polls/allcontent.html', {'userid': user,'eval':eval,'course':course,'score':score,'recom':recom,'posts':posts})
# def mycontent(request,userskku_id):
#     user = UserSKKU.objects.get(pk = userskku_id)
#
#     eval = Evaluation.objects.filter(user_id_id = userskku_id)
#
#     course = Course.objects.filter(user_id_id = userskku_id)
#
#     score = Score.objects.filter(user_id_id = userskku_id)
#
#     if request.method =="POST":
#         del_eval = Evaluation.objects.get(pk=request.POST['deleteID'])
#         del_cour = Course.objects.get(pk=request.POST['deleteID'])
#         del_score = Score.objects.get(pk=request.POST['deleteID'])
#         del_eval.delete()
#         del_cour.delete()
#         del_score.delete()
#     paginator = Paginator(course,3)
#     page=request.GET.get('page')
#     posts= paginator.get_page(page)
#     return render(request,'polls/mycontent.html', {'userid': user,'eval':eval,'course':course,'score':score,'posts':posts})
# def search(request,userskku_id):
#     return render(request,"polls/search.html")
# def search(request,userskku_id,search_id):
#     user = UserSKKU.objects.get(pk = userskku_id)
#
#     eval = Evaluation.objects.all()
#
#     course = Course.objects.all()
#
#     score = Score.objects.all()
#
#     likey = Likey.objects.all()
#
#     query = search_id
#     course_search = Course.objects.all().filter(Q(course_name_icontains=query))
#
#     return render(request,'polls/search.html', {'userid': user,'eval':eval,'course':course,'score':score,'likey':likey,'course_search':course_search})
