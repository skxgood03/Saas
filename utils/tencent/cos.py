from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
from django.conf import settings


def create_bucket(bucket, region='ap-chengdu'):
    """
    创建桶
    :param region: 区域
    :param Bucket: 桶名称
    :return:
    """
    # secret_id = ''  # 替换为⽤户的 secretId
    # secret_key = ''  # 替换为⽤户的 secretKey
    # region = 'ap-chengdu'  # 替换为⽤户的 Region
    token = None  # 使⽤临时密钥需要传⼊ Token，默认为空，可不填
    scheme = 'https'  # 指定使⽤ http/https 协议来访问 COS，默认为 https，可不填
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY,
                       Token=token, Scheme=scheme)
    # 2. 获取客户端对象
    client = CosS3Client(config)

    # 创建桶
    response = client.create_bucket(
        Bucket=bucket,  # 名称
        ACL='public-read',  # private(私有)/public-read(公读,私写)/public-read-write(公读,公写),

    )
    


def upload_file(bucket, region, file_object, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    # 2. 获取客户端对象
    client = CosS3Client(config)

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 文件对象
        Key=key  # 上传到桶之后的文件名
    )

    # 返回桶文件路径
    # https://wangyang-1251317460.cos.ap-chengdu.myqcloud.com/p1.png
    return 'https://{}.cos.{}.myqcloud.com/{}'.format(bucket, region, key)

