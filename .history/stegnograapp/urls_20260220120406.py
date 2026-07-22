from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('main/', views.main, name='main'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('admindash/', views.admindash, name='admindash'),
    path('content/', views.content, name='content'),
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('logout/', views.logout, name='logout'),
    path('userlist/', views.userlist, name='userlist'),
    path('deleteuser/<str:email>/', views.deleteuser, name='deleteuser'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('verify_register_otp/', views.verify_register_otp, name='verify_register_otp'),
]