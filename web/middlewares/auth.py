# 判断用户是否登陆中间件
import datetime
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import *
from web.models import *
from django.conf import settings


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddlewares(MiddlewareMixin):
    def process_request(self, request):
        '''如果用户已登录,则request中赋值'''
        request.saas = Tracer()

        user_id = request.session.get('user_id', 0)
        user_object = UserInfo.objects.filter(id=user_id).first()
        request.saas.user = user_object  # 当前登录的用户对象

        # 白名单:项目不登录就可以访问的页面URL
        '''
        1.获取用户当前访问的URL
        2.检查URL是否在白名单中,如果在,继续访问,如果在则判断是否登录
        '''
        if request.path_info in settings.WHITE_REGEX_URL_LIST:  # request.path_info获取当前访问URL
            return  # 中间件 默认return 空
        # 检查用户是否登录,已登录往前走,未登录返回登录页面
        if not request.saas.user:
            return redirect(reverse('login'))

        # 登录成功之后获取当前用户所拥有的额度
        # 免费额度在交易记录中储存
        # 获取当前用户ID值最大的(交易记录)
        _object = Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()

        # 判断是否已过期'
        current_datetime = datetime.datetime.now()
        if _object.end_datetime and _object.end_datetime < current_datetime:
            _object = Transaction.objects.filter(user=user_object, price_policy__category=1).first()


        request.saas.price_policy = _object.price_policy  # 当前登录用户的额度信息

    def process_view(self, request, view, args, kwargs):
        # 判断URl是否以manage开头,如果是，则项目ID是否是我创建 or 参与
        if not request.path_info.startswith('/manage/'):
            return
        project_id = kwargs.get('project_id')

        # 是否是我创建的
        project_object = Project.objects.filter(creator=request.saas.user, id=project_id).first()
        if project_object:
            # 是我创建的项目,我就让他通过
            request.saas.project = project_object
            return
        # 是否是我参与的
        project_user_object = ProjectUser.objects.filter(user=request.saas.user, project_id=project_id).first()
        if project_user_object:
            # 是我参与的项目,我就让他通过
            request.saas.project = project_user_object.project
            return
        return redirect('project_list')
