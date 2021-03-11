from django.db import models
from datetime import datetime
# Create your models here.
class UserDamoa(models.Model):
    user_name = models.CharField(max_length=25)
    user_id = models.CharField(max_length=20,primary_key=True)
    user_password = models.CharField(max_length=20)
    email = models.CharField(max_length=20,default='')
    report_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
class Product(models.Model):
    user_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.AutoField(primary_key=True)
    prod_name = models.CharField(max_length=50)
    place = models.CharField(max_length=100)
    now = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    phone = models.CharField(max_length=20)
    seller = models.CharField(max_length=20)
    category = models.CharField(max_length=20,default='')
    bid_unit = models.IntegerField(default=0)
    bid_start = models.DateTimeField(default=datetime.now())
    bid_end = models.DateTimeField(default=datetime.now())
    price = models.IntegerField()
    current_price = models.IntegerField(default=0)
    now_price = models.IntegerField(default=0)
    now_sold = models.IntegerField(default=0)
    now_buyer = models.CharField(max_length=20,default="")
    now_end = models.DateTimeField(default=datetime.now())
    likey = models.IntegerField(default=0)
    img = models.ImageField(upload_to='images/',default='')

    class Meta:
        unique_together = (('user_id', 'prod_id'),)
class WishList(models.Model):
    user_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    class Meta:
        unique_together = (('user_id', 'prod_id'),)
class AuctionHistory(models.Model):
    bid_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    bid_price = models.IntegerField(default = 0)
    bid_end = models.IntegerField(default = 0)
class Report(models.Model):
    user_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    prod_name =  models.CharField(max_length=50,default="")
    seller =  models.CharField(max_length=20)
    title = models.CharField(max_length=100,default="")
    content = models.CharField(max_length=500)
    reply = models.IntegerField(default = 0)
    reply_content = models.CharField(max_length=150,default="") 
class ShoppingList(models.Model):
    user_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    class Meta:
        unique_together = (('user_id', 'prod_id'),)
class Cart(models.Model):
    user_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    check = models.IntegerField(default = 0)
    now_price = models.IntegerField(default=0)
    class Meta:
        unique_together = (('user_id', 'prod_id'),)
class Inquiry(models.Model):
    user_id = models.ForeignKey(UserDamoa,max_length=20,on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Product,on_delete=models.CASCADE)
    prod_name =  models.CharField(max_length=50,default="")
    seller =  models.CharField(max_length=20)
    title = models.CharField(max_length=100,default="")
    content = models.CharField(max_length=500)
    reply = models.IntegerField(default = 0)
    reply_content = models.CharField(max_length=500,default="") 
# class Recommend(models.Model):
#     user_id = models.ForeignKey(UserSKKU,max_length=20,on_delete=models.CASCADE)
#     eval_id = models.ForeignKey(Evaluation,primary_key=True,on_delete=models.CASCADE)
#     recom_num = models.IntegerField(default=0)
#     class Meta:
#         unique_together = (('user_id', 'eval_id'),)
# class Score(models.Model):
#     user_id = models.ForeignKey(UserSKKU,max_length=20,on_delete=models.CASCADE)
#     eval_id = models.ForeignKey(Evaluation,primary_key=True,on_delete=models.CASCADE)
#     ass_difficulty = models.CharField(max_length=10)
#     test_difficulty = models.CharField(max_length=10)
#     teaching_ability = models.CharField(max_length=10)
#     total_score = models.CharField(max_length=10)
#     class Meta:
#         unique_together = (('user_id', 'eval_id'),)
