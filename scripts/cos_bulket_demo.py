#创建桶


# APPID 已在配置中移除,请在参数 Bucket 中带上 APPID。Bucket 由 BucketName-APPID 组成
# 1. 设置⽤户配置, 包括 secretId，secretKey 以及 Region
# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
secret_id = 'AKIDiBQYWGnni5XtBQNVAcv6Nlxxm272NXN1' # 替换为⽤户的 secretId
secret_key = 'fBWBg4pbFl7VpeJdv1g5nNiq5ezEJNoA' # 替换为⽤户的 secretKey
region = 'ap-chengdu' # 替换为⽤户的 Region
token = None # 使⽤临时密钥需要传⼊ Token，默认为空，可不填
scheme = 'https' # 指定使⽤ http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key,
Token=token, Scheme=scheme)
# 2. 获取客户端对象
client = CosS3Client(config)

# 创建桶
response = client.create_bucket(
 Bucket='text-1304763026' ,#名称
 ACL = 'public-read',  #private(私有)/public-read(公读,私写)/public-read-write(公读,公写),


)