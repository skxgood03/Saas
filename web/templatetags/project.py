from django.template import Library
from django.urls import reverse

from web.models import *

register = Library()

@register.inclusion_tag('inclusion/project_list.html')
def all_project_list(request):
    #1.获取我创建的所有项目
    my_Project_list=Project.objects.filter(creator=request.saas.user)
    #2.获取我参与的所有项目
    join_Project_list=ProjectUser.objects.filter(user=request.saas.user)
    return {'my':my_Project_list,'join':join_Project_list,'request':request}

@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(requerst):
    data_list = [
        {'title':'概述','url':reverse('dashboard',kwargs={'project_id':requerst.saas.project.id})},
        {'title':'问题','url':reverse('issues',kwargs={'project_id':requerst.saas.project.id})},
        {'title':'统计','url':reverse('statistics',kwargs={'project_id':requerst.saas.project.id})},
        {'title':'wiki','url':reverse('wiki',kwargs={'project_id':requerst.saas.project.id})},
        {'title':'文件','url':reverse('file',kwargs={'project_id':requerst.saas.project.id})},
        {'title':'配置','url':reverse('setting',kwargs={'project_id':requerst.saas.project.id})},
    ]

    for item  in data_list:
        #当前用户访问的URl加上class的active属性
        if requerst.path_info.startswith(item['url']):
            item['class']='active'
    return {'data_list':data_list}