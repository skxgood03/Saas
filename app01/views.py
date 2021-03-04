from django.shortcuts import *
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
# Create your views here.
#ModelForm表单
#优点1:#重写phone字段方法
from .models import *
from django import forms
from utils.tencent.sms import send_sms_single
import random
class RegModelFrom(forms.ModelForm):
    #重写phone字段方法正则匹配手机号格式,
    phone = forms.CharField(label='手机号',validators=[RegexValidator( "^((13[0-9])|(15[^4,\\D])|(18[0,0-9]))\\d{8}$",'手机浩格式错误')])
    #重写pwd方法,密文展示
    pwd = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"请输入密码"}),label='密码')
    pwds = forms.CharField(widget=forms.PasswordInput(),label='重复密码')
    code = forms.CharField(label='验证码')
    class Meta:
        model = UserInfo
        fields = ['name','Emi','pwd','pwds','phone','code']  #页面展示具体内容

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)

def red(request):
    form = RegModelFrom()
    return render(request, 'app01/red.html', {'form':form})


def send_sms(request):
    '''发送短信'''
    code = random.randrange(1000,9999)
    res = send_sms_single('17691394303',845994,[code,])

    print(res)
    return HttpResponse('发送成功')