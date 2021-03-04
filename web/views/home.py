import datetime

from django.shortcuts import *


from web.models import *


def index(request):
    return render(request, 'index.html')


def price(request):
    """套餐"""
    # 获取套餐
    policy_list = PricePolicy.objects.filter(category=2)
    return render(request, 'price.html', {'policy_list': policy_list})


def payment(request, policy_id):
    """支付页面"""
    # 1.价格策略（套餐）policy_id
    policy_object = PricePolicy.objects.filter(id=policy_id, category=2).first()
    if not policy_object:
        return redirect('price')
    # 2. 要购买的数量
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        return redirect('price')
    number = int(number)
    if number < 1:
        return redirect('price')

    # 3. 计算原价
    origin_price = number * policy_object.price

    # 4.之前购买过套餐(之前掏钱买过）
    balance = 0
    _object = None
    if request.saas.price_policy.category == 2:
        # 找到之前订单：总支付费用 、 开始~结束时间、剩余天数 = 抵扣的钱
        # 之前的实际支付价格
        _object = Transaction.objects.filter(user=request.saas.user, status=2).order_by('-id').first()
        total_timedelta = _object.end_datetime - _object.start_datetime
        balance_timedelta = _object.end_datetime - datetime.datetime.now()
        if total_timedelta.days == balance_timedelta.days:
            # 按照价值进行计算抵扣金额
            balance = _object.price_policy * price * _object.count / total_timedelta.days * (balance_timedelta.days - 1)
        else:
            balance = _object.price_policy * price * _object.count / total_timedelta.days * balance_timedelta.days

    if balance >= origin_price:
        return redirect('price')

    context = {
        'policy_id': policy_object.id,
        'number': number,
        'origin_price': origin_price,
        'balance': round(balance, 2),
        'total_price': origin_price - round(balance, 2)
    }
    # conn = get_redis_connection()
    # key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    # # conn.set(key, json.dumps(context), nx=60 * 30)
    # conn.set(key, json.dumps(context), ex=60 * 30)  # nx参数写错了，应该是ex（表示超时时间） ps：nx=True,表示redis中已存在key，再次执行时候就不会再设置了。
    #
    context['policy_object'] = policy_object
    context['transaction'] = _object

    return render(request, 'payment.html', context)
