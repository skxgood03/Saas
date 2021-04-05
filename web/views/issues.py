import datetime
import json

from django.shortcuts import render,reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from utils.encrypt import uid
from web.forms.issues import *
from django.http import *
from web.models import *
from utils.pagination import Pagination


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.data_list = data_list
        self.request = request
        self.name = name

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


# 通过可迭代对象实现筛选卡展示
class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.data_list = data_list
        self.request = request
        self.name = name

    def __iter__(self):
        for item in self.data_list:
            key = str(item[0])
            text = item[1]
            if text == "任务":
                text ='  <i class="fa fa-file" aria-hidden="true" style="color: #33cc66"></i> '+text
            if text == "功能":
                text ='  <i class="fa fa-cog" aria-hidden="true" style="color: #6666cc"></i> '+text
            if text == "Bug":
                text ='  <i class="fa fa-bug" aria-hidden="true" style="color: #330033"></i> '+text
            if text == "新建":
                text ='  <i class="fa fa-plus-square" aria-hidden="true" style="color: 	#9A32CD"></i> '+text
            if text == "处理中":
                text ='  <i class="fa fa-hourglass-end" aria-hidden="true" style="color: #FFFF00"></i> '+text
            if text == "已解决":
                text ='  <i class="fa fa-check-square" aria-hidden="true" style="color: #0099ff"></i> '+text
            if text == "已忽略":
                text ='  <i class="fa fa-eye-slash" aria-hidden="true" style="color:#1E1E1E"></i> '+text
            if text == "待反馈":
                text ='  <i class="fa fa-exclamation-circle" aria-hidden="true" style="color: #33cc66"></i> '+text
            if text == "已关闭":
                text ='  <i class="fa fa-toggle-off" aria-hidden="true" style="color: #33cc66"></i> '+text
            if text == "重新打开":
                text ='  <i class="fa fa-refresh" aria-hidden="true" style="color:#8968CD"></i> '+text
            if text == "高":
                text ='  <i class="fa fa-circle" aria-hidden="true" style="color: red"></i> '+text
            if text == "中":
                text ='  <i class="fa fa-circle" aria-hidden="true" style="color: #f1ea00"></i> '+text
            if text == "低":
                text ='  <i class="fa fa-circle" aria-hidden="true" style="color: #70B7FF"></i> '+text
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成URL
            ##在当前URl基础上去增加
            query_dict = self.request.GET.copy()
            query_dict._mutable = True  #加上Ｔｒｕｅ
            query_dict.setlist(self.name, value_list)  # {'status':[1,2..],'xx':[1,]}
            if 'page' in query_dict:
                query_dict.pop('page')

            # self.request.path_info+query_dict.urlencode() = http://127.0.0.1:8001/manage/20/issues/+status=1&status=2&xx=1
            url = "{}?{}".format(self.request.path_info, query_dict.urlencode())  # status=1&status=2&xx=1
            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label style="color: #3D3D3D" >{text}</label></a>'
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)


def issues(request, project_id):
    if request.method == 'GET':
        # 筛选条件(根据用户通过GET传过来的参数实现)
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # [1,2]
            if not value_list:
                continue
            condition["{}__in".format(name)] = value_list
        """
        condition = {
            "status__in":[1,2],
            'issues_type':[1,]
        }
        """
        # 分页获取数据
        queryset = Issues.objects.filter(project_id=project_id).filter(**condition)
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),  # 总数据
            base_url=request.path_info,
            query_params=request.GET,
            per_page=5
        )
        issues_object_list = queryset[page_object.start:page_object.end]

        form = IssuesModelForm(request)

        project_issues_type = IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')

        project_total_user = [(request.saas.project.creator_id, request.saas.project.creator.name,)]
        join_user = ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__name')
        project_total_user.extend(join_user)

        invite_form = InviteModelForm()
        context = {
            'form': form,
            'invite_form': invite_form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html(),
            'filter_list': [
                {'title': "类型", 'filter': CheckFilter('issues_type',project_issues_type, request)},
                {'title': "状态", 'filter': CheckFilter('status', Issues.status_choices, request)},
                {'title': "优先级", 'filter': CheckFilter('priority', Issues.priority_choices, request)},
                {'title': "指派", 'filter': SelectFilter('assign', project_total_user, request)},
                {'title': "关注", 'filter': SelectFilter('attention', project_total_user, request)},
            ]
        }
        return render(request, 'issues.html', context)
    # print(request.POST)
    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        # 手动赋值
        form.instance.project = request.saas.project
        form.instance.creator = request.saas.user
        # 添加问题
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    """编辑问题页面"""
    issues_object = Issues.objects.filter(id=issues_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issues_object)
    return render(request, 'issues_detail.html', {'form': form, 'issues_object': issues_object})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    '''初始话操作记录'''
    if request.method == 'GET':

        reply_list = IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.saas.project)

        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.name,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)
        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplModelFrom(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.saas.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.name,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    # 问题页面修改,数据库实时更新
    # 接收后台传过来的json数据
    issues_object = Issues.objects.filter(id=issues_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    """
    {'name': 'subject', 'value': '好饿呀sdfasdf'}
    {'name': 'subject', 'value': ''}
    
    {'name': 'desc', 'value': '好饿呀sdfasdf'}
    {'name': 'desc', 'value': ''}
    
    {'name': 'start_date', 'value': '好饿呀sdfasdf'}
    {'name': 'end_date', 'value': '好饿呀sdfasdf'}
    
    {'name': 'issues_type', 'value': '2'}
    {'name': 'assign', 'value': '4'}
    """
    # 1.数据库字段更新

    name = post_dict.get('name')
    value = post_dict.get('value')

    field_object = Issues._meta.get_field(name)  # 那取model字段

    def create_reply_record(content):
        """问题变更,实时显示"""
        new_object = IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.saas.user,
        )
        # 2.生成操作记录
        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.name,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }
        return new_reply_dict

    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            setattr(issues_object, name, None)
            issues_object.save()
            # 记录:xx更改为空
            change_record = "{}更改为空".format(field_object.verbose_name)
        else:
            setattr(issues_object, name, value)  # 反射
            issues_object.save()
            # 记录:xx更改为value
            change_record = "{}更改为：{}".format(field_object.verbose_name, value)
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # 1.2 Fk字段
    if name in ['issues_type', 'module', 'parent', 'assign']:
        # 用户选择为空
        if not value:
            # 不允许为空
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            # 允许为空
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = "{}更改为空".format(field_object.verbose_name)
        else:  # 用户输入不为空
            if name == 'assign':
                # 是否是项目创建者
                if value == str(request.saas.project.creator_id):
                    instance = request.saas.project.creator
                else:
                    project_user_object = ProjectUser.objects.filter(project_id=project_id, user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{}更改为：{}".format(field_object.verbose_name, str(instance))
            else:
                # 条件判断:用户输入的值是否是自己的
                instance = field_object.remote_field.model.objects.filter(id=value, project_id=project_id).first()  # 传进来的值,关联的对象
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{}更改为：{}".format(field_object.verbose_name, str(instance))

            return JsonResponse({'status': True, 'data': create_reply_record(change_record)})
    # 1.3 choices字段
    if name in ['priority', 'status', 'mode']:
        selected_text = None
        for key, text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': "您选择的值不存在"})

        setattr(issues_object, name, value)
        issues_object.save()
        change_record = "{}更新为：{}".format(field_object.verbose_name, selected_text)
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # M2M字段
    if name == "attention":
        # {"name":"attention","value":[1,2,3]}
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': "数据格式错误"})

        if not value:
            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:
            # values=["1","2,3,4]  ->   id是否是项目成员（参与者、创建者）
            # 获取当前项目的所有成员
            user_dict = {str(request.saas.project.creator_id): request.saas.project.creator.name}
            project_user_list = ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.name
            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}更新为{}".format(field_object.verbose_name, ",".join(username_list))

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    return JsonResponse({'status': False, 'error': "滚蛋"})

def invite_url(request, project_id, ):
    """生成验证码"""
    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建随机的邀请码
        2. 验证码保存到数据库
        3. 限制：只有创建者才能邀请
        """
        if request.saas.user != request.saas.project.creator:
            form.add_error('period', '无权创建邀请码')
            return JsonResponse({'status': False, 'error': form.errors})
        random_invite_codde = uid(request.saas.user.phone)
        form.instance.project = request.saas.project
        form.instance.code = random_invite_codde
        form.instance.creator = request.saas.user
        form.save()
        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme, #http/https
            host=request.get_host(), #主机端口
            path = reverse('invite_join',kwargs={'code':random_invite_codde})
        )
        return JsonResponse({'status':True,'data':url})
    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request,code):
    """访问邀请码"""
    current_datetime = datetime.datetime.now()
    invite_object = ProjectInvite   .objects.filter(code=code).first()
    if not invite_object:
        return render(request,'invite_join.html',{'error':'邀请码不存在'})
    if invite_object.project.creator == request.saas.user:
        return render(request, 'invite_join.html', {'error': '创建者无需再加入项目'})
    exists = ProjectUser.objects.filter(project=invite_object.project,user=request.saas.user).exists()
    if exists:
        return render(request, 'invite_join.html', {'error': '已加入项目无需再加入'})

    #最多允许的成员（）
    # max_member = request.saas.price_policy.project_member  #当前登录用户的限制
    #拿到项目创建者
    #是否已过期，如果已过期则使用免费额度
    max_transaction = Transaction.objects.filter(user=invite_object.project.creator).order_by('-id').first()
    if max_transaction.price_policy.category == 1:
        max_member = max_transaction.price_policy.project_member
    else:
        if max_transaction.end_datetime < current_datetime:
            free_object = PricePolicy.objects.filter(category=1).first()
            max_member = free_object.project_member
        else:
            max_member = max_transaction.price_policy.project_member

    # 目前所有成员(创建者&参与者）
    current_member = ProjectUser.objects.filter(project=invite_object.project).count()
    current_member = current_member + 1
    if current_member >= max_member:
        return render(request, 'invite_join.html', {'error': '项目成员超限，请升级套餐'})

    # 邀请码是否过期？

    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})

    #数量限制
    if invite_object.count:
        if invite_object.use_count >= invite_object.count:
            return render(request, 'invite_join.html', {'error': '邀请码数据已使用完'})
        invite_object.use_count += 1
        invite_object.save()

    ProjectUser.objects.create(user=request.saas.user, project=invite_object.project)

    # ####### 问题2： 更新项目参与成员 #######
    invite_object.project.join_count += 1
    invite_object.project.save()

    return render(request, 'invite_join.html', {'project': invite_object.project})


