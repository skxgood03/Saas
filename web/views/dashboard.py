import collections

from django.db.models import Count

from web.models import *
from django.shortcuts import render


def dashboard(request,project_id):
    """概揽"""
    #问题数据处理
    status_dict = collections.OrderedDict()
    for key,text in Issues.status_choices:
        status_dict[key] = {'text':text,'count':0}
    issues_data = Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    #项目成员
    user_list = ProjectUser.objects.filter(project_id=project_id).values('user_id','user__name')

    #动态（前十个指派问题）
    top_ten = Issues.objects.filter(project_id=project_id,assign__isnull=False).order_by('-id')[0:10]
    context = {
        'status_dict':status_dict,
        'user_list':user_list,
        'top_ten_object':top_ten
    }
    return render(request,'dashboard.html',context)
