from django.urls import path
from . import views
app_name='polls'
urlpatterns = [
    path('signup/',views.signup, name ='signup_new'),
    path('login/',views.login, name ='login_new'),
    path('index/<slug:which>',views.index, name ='index'),
    path('admin/',views.admin, name ='admin'),
    path('mypage/seller',views.mypage_seller, name ='mypage_seller'),
    path('mypage/seller/edit/<slug:prod_id>',views.mypage_seller_edit, name ='mypage_seller_edit'),
    path('mypage/wish',views.mypage_wish, name ='mypage_wish'),
    path('mypage/shoppinglist',views.mypage_shopping, name ='mypage_shopping'),
    path('mypage/cart',views.mypage_cart, name ='mypage_cart'),
    path('mypage/report',views.mypage_report, name ='mypage_report'),
    path('mypage/inquiry/buying',views.mypage_inquiry_buying, name ='mypage_inquiry_buying'),
    path('mypage/inquiry/selling',views.mypage_inquiry_selling, name ='mypage_inquiry_selling'),
    path('bidding/<slug:which>/<slug:prod_id>',views.bidding, name ='bidding'),
    path('counsel/<slug:which>/<slug:prod_id>',views.counsel, name ='counsel'),
    path('report/<slug:which>/<slug:prod_id>',views.report, name ='report'),
    path('admin/report/<slug:reported_id>',views.admin_report, name ='admin_report'),
    path('admin/report/reply/<slug:report_id>',views.admin_reply, name ='admin_reply'),
    path('admin/edit/<slug:user_id>',views.admin_edit, name ='admin_edit'),
    path('admin/userinfo/sales/<slug:user_id>',views.admin_userinfo_sales, name ='admin_userinfo_sales'),
    path('admin/userinfo/purchase/<slug:user_id>',views.admin_userinfo_purchase, name ='admin_userinfo_purchase'),
    path('account/login/kakao/', views.kakao_login, name='kakao_login'),
    path('oauth/',views.oauth,name='oauth'),
    # path('mypage/product/',views.mypage_product, name ='mypage_product'),
    # path('index/',views.logout, name ='logout'),
    path('home/<slug:which>',views.home, name ='home'),
    # path('auction/',views.auction, name ='auction'),
    path('register_product/',views.register, name ='register'),
    # path('<slug:userskku_id>/allcontent/',views.allcontent, name ='allcontent'),
    # path('<slug:userskku_id>/mycontent/',views.mycontent, name ='mycontent'),
    # path('<slug:userskku_id>/allcontent/',views.search, name ='search'),

    # path('index/<slug:which>',views.logout, name ='logout')
]
