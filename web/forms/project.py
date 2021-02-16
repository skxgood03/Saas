from django import forms
from .bootstrap import Bootstrap
from web.models import *
from django.core.exceptions import ValidationError
from .widgets import ColorRadioSelect

class ProjectMOdelFrom(Bootstrap, forms.ModelForm):
    bootstrap_class_exclude = ['color']
    class Meta:
        model = Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color':ColorRadioSelect(attrs={'class':'color-radio'})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        '''项目校验'''
        name = self.cleaned_data['name']  # 获取前端项目名
        # 1.当前用户是否已经创建过项目,项目名是否存在?
        # self.request.saas.user 中间件当前登录用户
        exists = Project.objects.filter(name=name, creator=self.request.saas.user).exists()
        if exists:
            raise ValidationError('项目已存在')
        # 2.当前用户是否还有额度创建项目
        # 最多创建项目
        # self.request.saas.price_policy.project_num
        # 当前用户现在创建多少项目
        count = Project.objects.filter(creator=self.request.saas.user).count()
        if count >= self.request.saas.price_policy.project_num:
            raise ValidationError('项目额度已用完,如需创建请购买套餐')
        return name
