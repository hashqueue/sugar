# Sugar - 一站式项目研发管理平台

权限控制基于RBAC，精确到菜单和按钮级别权限控制。

## 本地开发环境搭建
```shell
# cd到项目根目录，创建虚拟环境
virtualenv venv
source venv/bin/activate
pip3 install -i https://pypi.doubanio.com/simple -U pip
# 安装mysqlclient如果报错就去github仓库(https://github.com/PyMySQL/mysqlclient)查看readme文档查看如何安装缺失的相关依赖包
pip3 install -i https://pypi.doubanio.com/simple -r requirements.txt
# 使用docker快速启动一个MySQL8容器并设置密码为123456，并持久化数据到本地/home/hashqueue/mysqldatadir
docker run --name mysql8 -p 3306:3306 -v /home/hashqueue/mysqldatadir:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=123456 -d mysql:8.0.30
# 连接到数据库中，创建本地开发数据库
create database sugar_dev
# 进行数据迁移
ENV_PATH=./.env.dev python3 manage.py makemigrations
# 开发环境默认会找项目根目录下的.env.dev环境变量文件，所以debug=True模式下可以省略`ENV_PATH=./.env.dev`
python3 manage.py migrate
# 导入初始化数据
python3 manage.py loaddata init_db.json
# 启动项目
python3 manage.py runserver 0.0.0.0:8000
# 前端开发环境搭建见前端仓库 https://github.com/hashqueue/sugar-web.git
#####################################################
###                     celery                    ###
#####################################################
# 使用docker在本地快速启动一个rabbitmq服务器
# 15672：RabbitMQ 管理控制台端口，用于通过 Web 界面进行管理和监控 RabbitMQ 服务。
# 5672：RabbitMQ 的 AMQP 端口，用于客户端与 RabbitMQ 之间的通信。
# 1883：MQTT 协议的默认端口，RabbitMQ 也支持 MQTT 协议，并且可以通过该端口接收来自 MQTT 客户端的消息。
docker run -d --name ramq -p 5672:5672 -p 15672:15672 -p 1883:1883 -v /home/hashqueue/rabbitmq:/var/lib/rabbitmq rabbitmq:3.11-management-alpine
# 本地启动celery worker
celery -A sugar worker -l info
# 本地启动celery beat
celery -A sugar beat -l info
# 检查celery配置项是否正确，会直接修改settings.py文件
celery upgrade settings ./sugar/settings.py --django
#####################################################
###                     redis                     ###
#####################################################
# 本地启动一个Redis容器做测试用，持久化数据到本地/home/hashqueue/redisdata
docker run --name redis -d -p 6381:6379 -v /home/hashqueue/redisdata:/data redis:latest redis-server --save 180 1 --loglevel warning
#####################################################
###               Done!下边的命令了解即可            ###
#####################################################
# 生产环境下使用supervisor启动celery
ENV_PATH=./.env.prod supervisord -c celery_app.conf
# 进入supervisor控制台，支持很多命令行操作
ENV_PATH=./.env.prod supervisorctl -c celery_app.conf
# 生产环境使用开发服务器启动时手动指定读取哪个env文件(项目根目录下的.env.prod)
ENV_PATH=./.env.prod python3 manage.py runserver
# Django导出数据库数据
python3 manage.py dumpdata --format json --indent 2 -o init_db.json
# Django导入初始化数据到新的数据库中
python3 manage.py loaddata init_db.json
# 开发环境下使用daphne启动项目
daphne -b 0.0.0.0 -p 8000 sugar.asgi:application
# 生产环境下使用daphne启动项目
ENV_PATH=./.env.prod daphne -b 0.0.0.0 -p 8000 sugar.asgi:application
```
