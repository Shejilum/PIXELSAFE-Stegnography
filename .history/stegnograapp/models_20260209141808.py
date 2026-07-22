from django.db import models
class user(models.Model):
    image=models.ImageField(upload_to='profile/',null=True,blank=True)
    username=models.CharField(max_length=100,null=True,blank=True,unique=True)
    password=models.CharField(max_length=100,null=True,blank=True)
    confirmpassword=models.CharField(max_length=100,null=True,blank=True)
    email=models.EmailField(max_length=50,null=True,blank=True,unique=True)
    phone=models.IntegerField(null=True,blank=True,unique=True)
