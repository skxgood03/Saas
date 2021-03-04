from django.db import models
class UserInfo(models.Model):
    name = models.CharField(verbose_name='姓名',max_length=32)
    Emi = models.EmailField(verbose_name='邮箱',max_length=32)
    phone = models.CharField(verbose_name='手机号',max_length=32)
    pwd = models.CharField(verbose_name='密码',max_length=32)
