# Sugar - 集项目管理和测试管理于一体的一站式研发管理平台

权限控制基于RBAC，精确到菜单和按钮级别权限控制。

TODO

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
python3 manage.py runserver
# 前端开发环境搭建见前端仓库 https://github.com/hashqueue/sugar-web.git
#####################################################
###               Done!下边的命令了解即可            ###
#####################################################
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
