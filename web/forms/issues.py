from django import forms
from .bootstrap import Bootstrap
from web.models import *

class IssuesModelForm(Bootstrap,forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project','create_datetime','creator','latest_update_datetime']
        widgets = {
            'assign':forms.Select(attrs={'class':"seletepicker","data-live-search":"true"}),
            'attention':forms.SelectMultiple(attrs={'class':'selectpicker',"data-live-search":"true","data-actions-box":"true"}),
            'parent': forms.Select(attrs={'class': "seletepicker", "data-live-search": "true"}),
        }

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #处理数据初始化

        #1.获取当前项目的所有问题
        self.fields['issues_type'].choices = IssuesType.objects.filter(project=request.saas.project).values_list('id','title')

        #2.获取当前项目的所有模块
        module_list = [("","没有选中任何项"),]
        module_object_list = Module.objects.filter(project=request.saas.project).values_list('id','title')
        module_list.extend(module_object_list)
        self.fields['module'].choices = module_list

        #3.指派和关注者
        #数据库找到当前项目的参与者和创建者
        total_user_list = [(request.saas.project.creator_id,request.saas.project.creator.name),]
        project_user_list = ProjectUser.objects.filter(project=request.saas.project).values_list('user_id','user__name')

        total_user_list.extend(project_user_list)
        self.fields['assign'].choices = [("","没有选中任何项")] + total_user_list
        self.fields['attention'].choices = total_user_list

        #4.当前项目已创建的问题
        parent_list = [("","没有选中任何项")]
        parent_object_list = Issues.objects.filter(project=request.saas.project).values_list('id','subject')
        parent_list.extend(parent_object_list)
        self.fields['parent'].choices = parent_list






