from django.shortcuts import *
from django.http import *
from web.forms.project import *
from web.models import *
from utils.tencent.cos import create_bucket
import time


def project_list(request):
    '''项目列表'''
    if request.method == "GET":
        """
        1. 从数据库中获取两部分数据
            我创建的所有项目：已星标(star)、未星标
            我参与的所有项目：已星标、未星标
        2. 提取已星标
            列表 = 循环 [我创建的所有项目(my)] + [我参与的所有项目(join)] 把已星标的数据提取

        得到三个列表：星标、创建、参与
        """
        project_dict = {'star': [], 'my': [], 'join': []}
        my_project_list = Project.objects.filter(creator=request.saas.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({'value': row, 'type': 'my'})
            else:
                project_dict['my'].append(row)
        join_project_list = ProjectUser.objects.filter(user=request.saas.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({'value': item.project, 'type': 'join'})
            else:

                project_dict['my'].append(item.project)

        form = ProjectMOdelFrom(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})

    form = ProjectMOdelFrom(request, data=request.POST)
    if form.is_valid():
        name = form.cleaned_data['name']
        # 1.为项目创建cos桶
        bucket = "{}-{}-1304763026".format(request.saas.user.phone, str(int(time.time())))
        region = 'ap-chengdu'
        create_bucket(bucket,region)
        # 把桶和区域写入数据库
        form.instance.bucket = bucket
        form.instance.region = region
        # 验证通过:项目名,颜色,描述+creator谁创建的项目
        form.instance.creator = request.saas.user
        # 创建项目
        instance = form.save()
        #3.项目初始化问题类型
        issues_type_object_list = []
        for item in IssuesType.PROJECT_INIT_LIST:
            issues_type_object_list.append(IssuesType(project=instance,title=item))
        IssuesType.objects.bulk_create(issues_type_object_list) #批量增加
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    '''星标项目'''
    if project_type == 'my':
        Project.objects.filter(id=project_id, creator=request.saas.user).update(star=True)
        return redirect(reverse('project_list'))

    if project_type == 'join':
        ProjectUser.objects.filter(id=project_id, creator=request.saas.user).update(star=True)
        return redirect(reverse('project_list'))
    return HttpResponse('sss')


def project_unstar(request, project_type, project_id):
    '''取消星标'''
    if project_type == 'my':
        Project.objects.filter(id=project_id, creator=request.saas.user).update(star=False)
        return redirect(reverse('project_list'))

    if project_type == 'join':
        ProjectUser.objects.filter(id=project_id, creator=request.saas.user).update(star=False)
        return redirect(reverse('project_list'))
    return HttpResponse('sss')
