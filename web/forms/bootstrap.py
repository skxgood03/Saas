#这个类,作用:支持全部加bootstrap样式,也支持某个字段不加
class Bootstrap(object):
    #面向对象继承:同样的东西写在一个类里面,要用的话直接继承(类名)
    bootstrap_class_exclude = []
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            if name in self.bootstrap_class_exclude:  #如果名字在bootstrap_class_exclude列表里面,不加样式
                continue
            old_class = field.widget.attrs.get('class','')
            field.widget.attrs['class'] = '{} form-control'.format(old_class)
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)
