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
        return JsonResponse({'status':True,'data':data_list})

    form = IssuesReplModelFrom(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issues_id
        form.instance.reply_type = 2
        form.instance.creator = request.saas.user
        instance=form.save()
        info = {
                'id': instance.id,
                'reply_type_text': instance.get_reply_type_display(),
                'content': instance.content,
                'creator': instance.creator.username,
                'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': instance.reply_id
            }
        return JsonResponse({'status':True,'data':info})
    return JsonResponse({'status':False, 'error':form.errors})
