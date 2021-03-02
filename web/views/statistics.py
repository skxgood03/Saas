import collections

from django.db.models import Count
from django.shortcuts import *
from web.models import *
from django.http import JsonResponse
def statistics(request,project_id):
    """统计"""
    return render(request,'statistics.html')


def statistics_priority(request,project_id):
    """按照优先级生成饼图"""

    # 找到所有的问题，根据优先级分组，每个优先级的问题数量
    start = request.GET.get('start')
    end = request.GET.get('end')
    #1,构造字典
    data_dict = collections.OrderedDict()
    for key,text in Issues.priority_choices:
        data_dict[key] = {'name':text,'y':0}

    # 2.去数据查询所有分组得到的数据量
    result = Issues.objects.filter(project_id=project_id,
                                   create_datetime__gte=start,
                                   create_datetime__lt=end).values('priority').annotate(ct=Count('id'))

    # 3.把分组得到的数据更新到data_dict中
    for item in result:
        data_dict[item['priority']]['y'] = item['ct']
    return JsonResponse({'status':True,'data':list(data_dict.values())})


def statistics_project_user(request):
    return None