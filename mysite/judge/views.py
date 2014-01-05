# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template import loader,RequestContext,Context
from django.http import HttpResponse,HttpResponseRedirect
from judge.models import *
import datetime
from django.db import connection
def index(request):
    '''主界面'''
    t = loader.get_template("index.html")
    c = Context({})
    return HttpResponse(t.render(c))

def show_problem(request):
    '''problem界面'''
    problems = Problem.objects.all()
    t = loader.get_template("problem.html")
    c = Context({'problems':problems})
    return HttpResponse(t.render(c))

def top(request):
    '''页面的头部框架'''
    t = loader.get_template("top.html")
    c = Context({})
    return HttpResponse(t.render(c))

def hello(request):
    '''欢迎界面'''
    t = loader.get_template("hello.html")
    c = Context({})
    return HttpResponse(t.render(c))

def show_detail(request,id):
    '''显示题目的详细信息'''
    detail = Problem.objects.filter(problem_id=id)
    t = loader.get_template("detail.html")
    c = Context({'detail':detail[0]})
    return HttpResponse(t.render(c))

def problem_submit(request,id):
    '''题目提交'''
    t = loader.get_template("problemsubmit.html")
    c = RequestContext(request,{'id':id})
    return HttpResponse(t.render(c))
def problem_judge(request):
    '''接受提交并返回处理结果
        用可能会用到事物
        解决同时向两个表插入数据
        目前方法为先插一个，然后在插另一个
        user session
    '''
    user_id = '10086' 
    p_id = int(request.POST['id'])
    language = int(request.POST['language'])
    source = request.POST['source']
    cursor = connection.cursor()
    
    time = int(0)
    mem = int(0)
    result = 0#pending
    contest = 0#非比赛
    #插入到solution表一条记录
    sql = "insert into judge_solution (problem_id_id,user_id_id,time,memory,in_date,result,language,contest_id,defunct,code_length) \
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    param = (int(p_id),user_id,time,mem,datetime.datetime.now(),int(result),int(language),contest,0,len(source))
    cursor.execute(sql,param) 
    #插入到sourcecode表一条记录
    sql = "select solution_id from judge_solution where user_id_id=%s order by solution_id desc limit 1"
    param = (user_id)
    cursor.execute(sql,param)
    solution_id = int(cursor.fetchall()[0][0])
    
    sql = "insert into judge_sourcecode (solution_id_id,source)\
                                values(%s,%s)" 
    param =(solution_id,source)  
    cursor.execute(sql,param)
    return HttpResponseRedirect('/judge/status')

def show_status(request):
    '''status显示'''
    stus = Solution.objects.all()
    t = loader.get_template("status.html")
    c = RequestContext(request,{'stus':stus})
    return HttpResponse(t.render(c))

def show_source(request,id):
    '''显示提交的源代码'''
    t = loader.get_template("showsource.html")
    source = Sourcecode.objects.filter(solution_id_id=id)
    c = Context({'source':source[0]})
    return HttpResponse(t.render(c))
def show_compileinfo(request,id):
    '''显示编译错误'''
    t = loader.get_template("showcompileinfo.html")
    compileinfo = Compileinfo.objects.filter(solution_id_id=id)
    c = Context({'compileinfo':compileinfo[0]})
    return HttpResponse(t.render(c))
    
