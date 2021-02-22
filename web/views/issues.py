from django.shortcuts import render
from web.forms.issues import *
from django.http import *
from web.models import *

def issues(request,project_id):
    if request.method == 'GET':
        form = IssuesModelForm(request)
        Issues_object_list = Issues.objects.filter(project_id=project_id)
        return render(request,'issues.html',{'form':form,'issues_object_list':Issues_object_list})
    # print(request.POST)
    form = IssuesModelForm(request,data = request.POST)
    if form.is_valid():
        #手动赋值
        form.instance.project = request.saas.project
        form.instance.creator = request.saas.user
        #添加问题
        form.save()
        return JsonResponse({'status':True})

    return JsonResponse({'status':False,'error':form.errors})
