import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from web.forms.issues import *
from django.http import *
from web.models import *
from utils.pagination import Pagination


def issues(request, project_id):
    if request.method == 'GET':
        # 分页获取数据
        queryset = Issues.objects.filter(project_id=project_id)
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),  # 总数据
            base_url=request.path_info,
            query_params=request.GET,
            per_page=1
        )
        Issues_object_list = queryset[page_object.start:page_object.end]
        form = IssuesModelForm(request)
        return render(request, 'issues.html',
                      {'form': form, 'issues_object_list': Issues_object_list, 'page_html': page_object.page_html()})
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
                'creator': row.creator.username,
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
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})

@csrf_exempt
def issues_change(request, project_id, issues_id):
    # 问题页面修改,数据库实时更新
    # 接收后台传过来的json数据
    issues_object = Issues.objects.filter(id=issues_id,project_id=project_id).first()
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
    #1.数据库字段更新

    name = post_dict.get('name')
    value = post_dict.get('value')

    field_object = Issues._meta.get_field(name)#那取model字段
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
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }
        return new_reply_dict
    if name in ['subject','desc','start_date','end_date']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status':False,'error':"您选择的值不能为空"})
            setattr(issues_object,name,None)
            issues_object.save()
            #记录:xx更改为空
            change_record= "{}更改为空".format(field_object.verbose_name)
        else:
            setattr(issues_object,name,value) #反射
            issues_object.save()
            #记录:xx更改为value
            change_record = "{}更改为{}".format(field_object.verbose_name,value)
        return JsonResponse({'status':True,'data':create_reply_record(change_record)})
    #1.2 Fk字段
    if name in ['issues_type','module','parent','assign']:
        #用户选择为空
        if not value:
            #不允许为空
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "您选择的值不能为空"})
            #允许为空
            setattr(issues_object,name,None)
            issues_object.save()
            change_record = "{}更改为空".format(field_object.verbose_name)
        else:#用户输入不为空
            if name == 'assign':
                #是否是项目创建者
                if value == str(request.saas.project.creator_id):
                    instance = request.saas.project.creator
                else:
                    project_user_object = ProjectUser.objects.filter(project_id=project_id,user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})
                setattr(issues_object,name,instance)
                issues_object.save()
                change_record = "{}更改为{}".format(field_object.verbose_name, str(instance))
            else:
                #条件判断:用户输入的值是否是自己的
                instance = field_object.rel.model.objects.filter(id=value,project_id=project_id).first() #传进来的值,关联的对象
                if not instance:
                    return JsonResponse({'status': False, 'error': "您选择的值不存在"})
                setattr(issues_object,name,instance)
                issues_object.save()
                change_record = "{}更改为{}".format(field_object.verbose_name, str(instance))

            return JsonResponse({'status':True,'data':create_reply_record(change_record)})
    # 1.3 choices字段
    if name in  ['priority','status','mode']:
        selected_text = None
        for key,text in field_object.choices:
            if str(key)== value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': "您选择的值不存在"})

        setattr(issues_object,name,value)
        issues_object.save()
        change_record = "{}更改为{}".format(field_object.verbose_name, selected_text )

    #M2M字段
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
            user_dict = {str(request.saas.project.creator_id): request.saas.project.creator.username}
            project_user_list = ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username
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

    return JsonResponse({'status': False, 'error': "滚"})
