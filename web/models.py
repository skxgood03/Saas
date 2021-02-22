from django.db import models
class UserInfo(models.Model):
    name = models.CharField(verbose_name='姓名',max_length=32)
    Emi = models.EmailField(verbose_name='邮箱',max_length=32)
    phone = models.CharField(verbose_name='手机号',max_length=32)
    pwd = models.CharField(verbose_name='密码',max_length=32)

    def __str__(self):
        return self.name

class PricePolicy(models.Model):
    """ 价格策略 """
    category_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题', max_length=32)
    price = models.PositiveIntegerField(verbose_name='价格')  # 正整数

    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数')
    project_space = models.PositiveIntegerField(verbose_name='单项目空间', help_text='G')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小', help_text="M")

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    """ 交易记录 """
    status_choice = (
        (1, '未支付'),
        (2, '已支付')
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choice)

    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)  # 唯一索引

    user = models.ForeignKey(UserInfo,verbose_name='用户',on_delete=models.CASCADE)
    price_policy = models.ForeignKey(PricePolicy,verbose_name='价格策略', on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name='数量（年）', help_text='0表示无限期')

    price = models.IntegerField(verbose_name='实际支付价格')

    start_datetime = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Project(models.Model):
    """ 项目表 """
    COLOR_CHOICES = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )

    name = models.CharField(verbose_name='项目名', max_length=32)
    color = models.SmallIntegerField(verbose_name='颜色', choices=COLOR_CHOICES, default=1)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)

    use_space = models.BigIntegerField(verbose_name='项目已使用空间', default=0, help_text='字节')

    star = models.BooleanField(verbose_name='星标', default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(UserInfo,verbose_name='创建者',on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='cos桶', max_length=128)
    region = models.CharField(verbose_name='cos区域', max_length=32)

    # 查询：可以省事；
    # 增加、删除、修改：无法完成
    # project_user = models.ManyToManyField(to='UserInfo',through="ProjectUser",through_fields=('project','user'))


class ProjectUser(models.Model):
    """ 项目参与者 """
    project = models.ForeignKey(Project,verbose_name='项目', on_delete=models.CASCADE)
    user = models.ForeignKey(UserInfo,verbose_name='参与者', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标', default=False)

    create_datetime = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


class WiKi(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='项目')
    title = models.CharField(verbose_name='标题',max_length=32)
    content = models.TextField(verbose_name='内容')
    depth = models.IntegerField(verbose_name='深度',default=1)
    #子关联(外建链接本身id)
    parent = models.ForeignKey('self',verbose_name='副文章',on_delete=models.CASCADE,null=True,blank=True,related_name='children')

    def __str__(self):
        return self.title


class FileRepository(models.Model):
    '''文件库'''
    project = models.ForeignKey('Project',verbose_name='项目',on_delete=models.CASCADE)
    file_type_choices = (
        (1,'文件'),
        (2,'文件夹')
    )
    file_type = models.SmallIntegerField(verbose_name='类型',choices=file_type_choices)
    name = models.CharField(verbose_name='文件夹名称', max_length=32, help_text="文件/文件夹名")
    key = models.CharField(verbose_name='文件储存在COS中的KEY', max_length=128, null=True, blank=True)

    # int类型最大表示的数据
    file_size = models.BigIntegerField(verbose_name='文件大小', null=True, blank=True, help_text='字节')

    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True,
                                 blank=True)  # https://桶.cos.ap-chengdu/....

    parent = models.ForeignKey('self',verbose_name='父级目录',  related_name='child', null=True, blank=True,on_delete=models.CASCADE)

    update_user = models.ForeignKey('UserInfo', verbose_name='最近更新者',on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)


class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey( 'Project',verbose_name='项目',on_delete=models.CASCADE)
    issues_type = models.ForeignKey('IssuesType',verbose_name='问题类型',on_delete=models.CASCADE)
    module = models.ForeignKey('Module',verbose_name='模块', null=True, blank=True,on_delete=models.CASCADE)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey('UserInfo',verbose_name='指派', related_name='task', null=True, blank=True,on_delete=models.CASCADE)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey('self', verbose_name='父问题',related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey('UserInfo', verbose_name='创建者',related_name='create_problems',on_delete=models.CASCADE)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class Module(models.Model):
    """ 模块（里程碑）"""
    project = models.ForeignKey('Project',verbose_name='项目',on_delete=models.CASCADE)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class IssuesType(models.Model):
    """ 问题类型 例如：任务、功能、Bug """

    PROJECT_INIT_LIST = ["任务", '功能', 'Bug']

    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey('Project',verbose_name='项目',on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class IssuesReply(models.Model):
    """ 问题回复"""

    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    reply_type = models.IntegerField(verbose_name='类型', choices=reply_type_choices)

    issues = models.ForeignKey('Issues',verbose_name='问题',on_delete=models.CASCADE)
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey('UserInfo',verbose_name='创建者', related_name='create_reply',on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey('self',verbose_name='回复', null=True, blank=True,on_delete=models.CASCADE)