python-judge-online
===================

python ACM judge online python(ACM在线判题系统) 
现在仅支持C/C++/java的题目

mysite为显示题目和比赛的django程序
core 为本地判题的程序
mysite的启用是使用：
首先打开mysql穿件数据库：
create database djangodb charset utf8;
然后同步数据库
cd mysite
python manage.py syncdb   #会提示创建超级用户
启动服务器
python manage.py runserver
后台默认为127.0.0.1:8000/admin    账户密码就是你更新数据库是创建的超级用户
core使用前请修改所有文件的oj_home为core当前所在的目录然后：
pyton main.py start即可

如果想添加数据只需在前台添加题目描述，后台core文件夹data下添加对应的标准输入输出即可。
由于时间短，本oj仅仅达到了运行的目的，很多异常和bug没有处理，请大家随便改。
如有问题请联系QQ：913614263


