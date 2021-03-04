from django.contrib import admin
from django.urls import path,include
from app01 import views
urlpatterns = [
    path('red/',views.red,name= 'red'),
    path('send/',views.send_sms,name= 'red'),
]