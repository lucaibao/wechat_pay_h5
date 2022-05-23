# h5_pay
瑞合收款H5

1.概述 

    瑞合收款H5--接入微信支付
    http服务采用架构为gunicorn服务器,数据库使用mysql

2.目录结构说明

```
app                         应用程序
api/__init__.py             应用程序的创建和配置
api/hooks.py                钩子函数
api/models.py               orm对象
api/view                    视图
api/model                   处理函数
common                      公共模块
common/json_data.py         封装返回数据
common/status_code.py       返回状态码
doc                         存放域名安全校验文件
util                        工具相关
util/log_.py                生成日志对象
util/mysql_.py              生成数据库的db对象
util/redis_.py              生成redis操作对象
logs                        存放日志文件
setting.py                  配置文件
docker-compose.yml          容器启动服务相关配置
Dockerfile                  容器启动相关环境
main.py                     启动文件
requirements.txt            依赖的第三方模块
README.md                   README
```
