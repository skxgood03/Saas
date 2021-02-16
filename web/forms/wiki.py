from django import forms

from web.models import *
from web.forms.bootstrap import Bootstrap


class WikiModelFrom(Bootstrap, forms.ModelForm):
    class Meta:
        model = WiKi
        exclude = ['project','depth']  # 反向操作,移除project字段,显示其他

    # 修副副文本全部展示的bug
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 找到想要的字段把他绑定显示的数据重置
        # 数据 = 去数据库中获取当前项目所有的wiki标题
        total_data_list = [('', '请选择'), ]
        data_list = WiKi.objects.filter(project=request.saas.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list
