#项目管理
from django.shortcuts import *
def dashboard(request,project_id):
    return render(request,'dashboard.html')


def issues(request,project_id):
    return render(request,'issues.html')


def file(request,project_id):
    return render(request,'file.html')







def statistics(request,project_id):
    return render(request,'statistics.html')