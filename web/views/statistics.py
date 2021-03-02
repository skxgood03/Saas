
from django.shortcuts import *

def statistics(request,project_id):
    """统计"""
    return render(request,'statistics.html')