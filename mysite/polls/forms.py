from django import forms 
from .models import *
  
class ProductForm(forms.ModelForm): 
  
    class Meta: 
        model = Product 
        fields = ['user_id', 'prod_id','prod_name','place','now','sold','phone','seller','category','price','img'] 