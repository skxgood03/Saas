from django import forms
from web.models import *
from web.forms.bootstrap import Bootstrap
from django.core.exceptions import ValidationError


class FileFolderModelForm(Bootstrap, forms.ModelForm):
    class Meta:
        model = FileRepository
        fields = ['name']

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    def clean_name(self):
        name = self.cleaned_data['name']

        # 数据库判断当前目录,文件夹名是否有重复
        queryset = FileRepository.objects.filter(file_type=2, name=name,project=self.request.saas.project)
        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists = queryset.filter(parent__isnull = True).exists()
        if exists:
            raise ValidationError('文件夹名重复')
        return name

