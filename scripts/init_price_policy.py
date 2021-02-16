# 创建离线脚本(运行单个py文件,达到相应需求,不用运行整个django框架)
import base
#往数据库添加价格策略
from web.models import *
def run():
    exists = PricePolicy.objects.filter(category=1,title='个人免费版' ).exists()
    if not exists :
        PricePolicy.objects.create(
            category=1,
            title='个人免费版',
            price=0,
            project_num=3,
            project_member=2,
            project_space=20,
            per_file_size=5

        )

if __name__ == '__main__':
    run()
