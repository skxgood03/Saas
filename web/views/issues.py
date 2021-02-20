from django.shortcuts import render


def issues(request,project_id):
    return render(request,'issues.html')