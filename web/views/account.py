'''
用户账户相关功能:注册 短信 登录 注销
'''
import datetime
import uuid #随机字符串

from django.shortcuts import *
from django.http import *
from web.forms.account import *
from django_redis import get_redis_connection


def register(request):
    if request.method == 'GET':
        forms = RegModelFrom()
        return render(request, 'register.html', {'form': forms})
    form = RegModelFrom(data=request.POST)
    if form.is_valid():
        # 验证通过,写入数据库(密码密文)
        # instance = UserInfo.objects.create(**form.cleaned_data)
        instance = form.save()  # save()自动去除数据库没有的字段 如:重复密码,验证码
        policy_object =  PricePolicy.objects.filter(category=1, title='个人免费版').first()
        #创建交易记录
        Transaction.objects.create(
            status=2,
            #订单(随机字符串)
            order=str(uuid.uuid4()),
            user=instance,
            price_policy = policy_object,
            count=0,
            price= 0,
            start_datetime=datetime.datetime.now()

        )
        return JsonResponse({'status': True, 'data': '/login/'})
    else:
        print(form.errors)
    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    """ 发送短信 """
    form = SendSmsForm(request, data=request.GET)
    phone = request.GET.get('phone')
    # 只是校验手机号：不能为空、格式是否正确
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if form.is_valid():
        # 所有验证通过发送短信
        code = random.randrange(1000, 9999)
        sms = send_sms_single(phone, template_id, [code, ])
        if sms['result'] != 0:
            form.add_error("短信发送失败，{}".format(sms['errmsg']),sms['errmsg'])
        # 存入redis
        conn = get_redis_connection()
        conn.set(phone, code, ex=60)
        print('判断缓存中是否有:', conn.type(phone))
        print('获取Redis验证码:', conn.get(phone))
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})

def login_sms(request):
    '''短信登录'''
    if request.method == 'GET':
        forms = LoginSMSForm()
        return render(request, 'login_sms.html', {'form': forms})

    form = LoginSMSForm(data=request.POST)
    if form.is_valid():
        # 用户正确,登录成功
        user_object = form.cleaned_data['phone']
        # 将用户信息存入session
        request.session['user_id'] = user_object.id
        request.session.set_expiry(60 * 60 * 24 * 14)

        return JsonResponse({'status': True, 'data': '/index/'})

    return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    '''用户名密码登录'''
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'login.html', {'form': form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']

        pwd = form.cleaned_data['pwd']

        # user_object = UserInfo.objects.filter(name=name,pwd=pwd).first()
        from django.db.models import Q

        user_object = UserInfo.objects.filter(Q(Emi=name) | Q(phone=name)).filter(
            pwd=pwd).first()

        if user_object:
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60 * 60 * 24 * 14)
            return redirect(reverse('index'))
        form.add_error('name', '用户名或者密码错误')
    return render(request, 'login.html', {'form': form})


def image_code(request):
    '''生成图片验证码'''
    from io import BytesIO
    from utils.image_code import check_code

    image_object, code = check_code()
    request.session['image_code'] = code
    request.session.set_expiry(60)  # 设置验证码过期时间,为60秒
    stream = BytesIO()
    image_object.save(stream, 'png')
    stream.getvalue()
    return HttpResponse(stream.getvalue())


def loginout(request):
    request.session.flush() #清除session内容

    return redirect(reverse('index'))