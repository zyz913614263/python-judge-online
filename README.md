python-judge-online
===================

python ACM judge online python(ACM在线判题系统) 


mysite为显示题目和比赛的django程序
core 为本地判题的程序
mysite的启用是使用：
cd mysite
python manage.py runserver
core使用前请修改所有文件的oj_home为core当前所在的目录然后：
pyton main.py start即可

如果想添加数据只需在前台添加题目描述，后台core文件夹下添加对应的标准输入输出即可。
