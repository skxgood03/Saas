from django.shortcuts import *
from utils.tencent.cos import delete_bucket
from web.models import Project


def setting(request,project_id):
    return render(request,'setting.html')


def setting_delete(request,project_id):
    """删除项目"""
    if request.method == 'GET':
        return render(request,'setting_delete.html')

    project_name = request.POST.get('project_name')
    if not project_name or project_name != request.saas.project.name:
        return render(request, 'setting_delete.html',{'error':'项目名错误'})

    #项目名对了删除(只有创建者可以删除)
    if request.saas.user != request.saas.project.creator:
        return render(request, 'setting_delete.html',{'error':'本项目只有创建者才可以删除'})

    #1.删除桶(先删除文件(和碎片),才可以删除桶),
    #2.删除项目
    delete_bucket(request.saas.project.bucket,request.saas.project.region)
    Project.objects.filter(id=request.saas.project.id).delete()
    return redirect('project_list')