#项目管理
from django.shortcuts import *





def file(request,project_id):
    return render(request,'file.html')







def statistics(request,project_id):
    return render(request,'statistics.html')