#account视图所有的表单信息
import random
from utils import encrypt
from web.models import *
from django.conf import settings
from django.shortcuts import render
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from utils.tencent.sms import send_sms_single
from django_redis import get_redis_connection
# Create your views here.
#ModelForm表单
#优点1:#重写phone字段方法
from web.models import *
from django import forms
from .bootstrap import Bootstrap #引入Bootstrap
#注册From
class RegModelFrom(Bootstrap,forms.ModelForm):
    #重写pwd方法,密文展示
    pwd = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':"请输入密码"}),
                          label='密码',
                          min_length=8,
                          max_length=64,
                          error_messages={
                              'min_length':'密码长度不能小于8个字符',
                              'max_length':'密码长度不能大于64个字符',
                          })
    pwds = forms.CharField(widget=forms.PasswordInput(),label='重复密码',
                           min_length=8,
                           max_length=64,
                           error_messages={
                               'min_length': '重复密码长度不能小于8个字符',
                               'max_length': '重复密码长度不能大于64个字符',
                           })
    #重写phone字段方法正则匹配手机号格式,
    phone = forms.CharField(label='手机号',validators=[RegexValidator( r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误')])
    code = forms.CharField(label='验证码')
    class Meta:
        model = UserInfo
        fields = ['name','Emi','pwd','pwds','phone','code']  #页面展示具体内容

    def clean_name(self):
        name = self.cleaned_data['name']
        exists  = UserInfo.objects.filter(name=name).exists()
        if exists:
            raise ValidationError('用户名已存在')
        return name
    def clean_Emi(self):
        Emi = self.cleaned_data['Emi']
        exists  = UserInfo.objects.filter(Emi=Emi).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return Emi
    def clean_pwd(self):
        pwd = self.cleaned_data['pwd']
        #加密&返回
        return encrypt.md5(pwd)
    def clean_pwds(self):
        #判断两次密码是否一致
        pwd = self.cleaned_data.get('pwd')
        pwds = encrypt.md5(self.cleaned_data['pwds'])
        if pwd !=pwds:
            raise ValidationError('两次密码不一致')
        return pwds
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        exists  = UserInfo.objects.filter(phone=phone).first()
        if exists:
            raise ValidationError('手机号已注册')
        return phone
    def clean_code(self):
        code = self.cleaned_data['code']
        # phone = self.cleaned_data['phone']
        phone = self.cleaned_data.get('phone')
        if not phone:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(phone)
        if not redis_code:
            raise ValidationError('验证码失效或者未发送,请重新发送')
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误,请重新输入')
        return code
#发送短信
class SendSmsForm(forms.Form):

    phone = forms.CharField(label='手机号', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_phone(self):
        """ 手机号校验的钩子 """
        phone = self.cleaned_data['phone']

        # 判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            # self.add_error('mobile_phone','短信模板错误')
            raise ValidationError('短信模板错误')

        exists = UserInfo.objects.filter(phone=phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError('手机号未注册')
        else:
            # 校验数据库中是否已有手机号
            if exists:
                raise ValidationError('手机号已注册')

        # code = random.randrange(1000, 9999)

        # 发送短信
        # sms = send_sms_single(phone, template_id, [code, ])
        # if sms['result'] != 0:
        #     raise ValidationError("短信发送失败，{}".format(sms['errmsg']))

        # 验证码 写入redis（django-redis）
        # conn = get_redis_connection()
        # conn.set(phone, code, ex=60)

        return phone

#短信登录form
class LoginSMSForm(Bootstrap,forms.Form):

    phone = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'),]
    )
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # exists = UserInfo.objects.filter(phone=phone).exists()
        user_object = UserInfo.objects.filter(phone=phone).first()
        if not user_object:
            raise ValidationError('手机号未注册')
        return phone

    def clean_code(self):
        code = self.cleaned_data['code']
        # phone = self.cleaned_data['phone']
        user_object = self.cleaned_data.get('phone')
        if not user_object:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(user_object.phone)
        if not redis_code:
            raise ValidationError('验证码失效或者未发送,请重新发送')
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误,请重新输入')
        return code


class LoginForm(Bootstrap,forms.Form):
    name = forms.CharField(label='邮箱或者手机号')
    pwd = forms.CharField(label='密码',widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_pwd(self):
        pwd = self.cleaned_data['pwd']
        #加密&返回
        return encrypt.md5(pwd)

    def clean_code(self):
        '''钩子 验证码是否正确'''
        code  = self.cleaned_data['code']

        #去session获取自己的验证码
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('验证码已过期,请重新输入')

        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError('验证码错误,请重新输入')
        return code


