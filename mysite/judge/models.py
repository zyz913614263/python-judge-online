# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
import datetime
class Problem(models.Model):
    '''题目表'''
    problem_id = models.AutoField('题目编号',primary_key=True,blank=False,unique=True)
    title = models.CharField(max_length=200,blank=False)
    description = models.TextField(blank=True,null=True)
    input = models.TextField(blank=True,null=True)
    output = models.TextField(blank=True,null=True)
    sample_input = models.TextField(blank=True,null=True)
    sample_output = models.TextField(blank=True,null=True)
    spj = models.BooleanField('special judge',default=False)
    hint = models.TextField(blank=True,null=True)
    source = models.CharField(max_length=100,blank=True,null=True)
    in_date = models.DateTimeField('时间',default = datetime.datetime.now(),null=True)
    time_limit = models.IntegerField('time limit (ms)',blank=False)
    memory_limit = models.IntegerField('memory limit (kb)',blank=False)
    defunct = models.BooleanField('是否屏蔽',default=False)
    accepted = models.IntegerField(blank=True,default=0,null=True)
    submit = models.IntegerField(blank=True,default=0,null=True)
    def __unicode__(self):
        return unicode(self.problem_id)
    
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('problem_id','title')
    
admin.site.register(Problem,ProblemAdmin)

class User(models.Model):
    '''用户表'''
    user_id = models.CharField(max_length=20,blank=False,null=False,primary_key=True,unique=True)
    email = models.CharField(max_length=100,blank=True,null=True)
    submit = models.IntegerField(blank=True,null=True,default=0)
    solved = models.IntegerField(blank=True,null=True,default=0)
    defunct = models.BooleanField('是否屏蔽',default=False)
    accesstime = models.DateTimeField('登录时间',default=datetime.datetime.now(),null=True,blank=True)
    language = models.IntegerField('语言',blank=False,null=False)
    password = models.CharField(max_length=32,blank=False,null=False)
    reg_time = models.DateTimeField('注册时间',default=datetime.datetime.now(),null=True,blank=True)
    nick = models.CharField(max_length=100,blank=False,null=False)
    school = models.CharField(max_length=100,blank=False,null=False)
    grade = models.SmallIntegerField(blank=True,null=True)
    major = models.CharField(max_length=50,blank=True,null=True)
    _class = models.SmallIntegerField(blank=True,null=True)
    def __unicode__(self):
        return unicode(self.user_id)
    
class UserAdmin(admin.ModelAdmin):
    list_display=('user_id','nick','school')

admin.site.register(User,UserAdmin)

class Contest(models.Model):
    '''比赛信息'''
    contest_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User)
    title = models.CharField(max_length=255,blank=True,null=True)
    start_time = models.DateTimeField(blank=True,null=True,default=datetime.datetime.now())
    end_time = models.DateTimeField(blank=True,null=True,default=datetime.datetime.now())
    defunct = models.BooleanField('是否屏蔽',default=False)
    description = models.TextField(blank=True,null=True)
    private = models.BooleanField(default=0)
    langmadk = models.IntegerField(blank=True,null=True)
    password = models.CharField(max_length=100,blank=True,null=True)
    def __unicode__(self):
        return unicode(self.contest_id)
    
class ContestAdmin(admin.ModelAdmin):
    list_display=('contest_id','user_id','title','description')
admin.site.register(Contest,ContestAdmin)

class Solution(models.Model):
    '''程序运行结果记录'''
    solution_id = models.AutoField(primary_key=True)
    problem_id = models.ForeignKey(Problem)
    user_id = models.ForeignKey(User)
    time = models.IntegerField(blank=False,null=False,default=0)
    memory = models.IntegerField(blank=False,null=False,default=0)
    in_date = models.DateTimeField('加入时间',blank=False,null=False,default=datetime.datetime.now())
    result = models.SmallIntegerField(blank=False,null=False)
    language = models.IntegerField(blank=False,null=False)
    contest_id = models.IntegerField(blank=True,null=True,default=0)
    defunct = models.BooleanField('是否屏蔽',default=False)
    num = models.SmallIntegerField(blank=True,null=True,default=0)
    code_length = models.IntegerField(blank=False,null=False)
    def __unicode__(self):
        return unicode(self.solution_id)
    class Meta:
        ordering = ('-solution_id',)
    
class SolutionAdmin(admin.ModelAdmin):
    list_display=('solution_id','problem_id','user_id','time','memory','result')
    
admin.site.register(Solution,SolutionAdmin)

class Runtimeinfo(models.Model):
    '''运行错误信息（Runtime Error）'''
    solution_id = models.ForeignKey(Solution)
    error = models.TextField(blank=True,null=True)

class RuntimeinfoAdmin(admin.ModelAdmin):
    list_display=('solution_id','error')
admin.site.register(Runtimeinfo,RuntimeinfoAdmin)

class Sourcecode(models.Model):
    '''记录源代码'''
    solution_id = models.ForeignKey(Solution)
    source = models.TextField(blank=True,null=True)
class SourcecodeAdmin(admin.ModelAdmin):
    list_display=('solution_id','source')
admin.site.register(Sourcecode, SourcecodeAdmin)

class Compileinfo(models.Model):
    '''编译信息（Compile Error）'''
    solution_id = models.ForeignKey(Solution)
    error = models.TextField(blank=True,null=True)

class CompileinfoAdmin(admin.ModelAdmin):
    list_display=('solution_id','error')
admin.site.register(Compileinfo,CompileinfoAdmin)

class Sim(models.Model):
    '''编译信息（Compile Error）'''
    s_id = models.ForeignKey(Solution)
    sim_s_id = models.IntegerField(blank=True,null=True)
    sim =  models.IntegerField(blank=True,null=True)
class SimAdmin(admin.ModelAdmin):
    list_display=('s_id','sim_s_id','sim')
admin.site.register(Sim,SimAdmin)

class Contestproblem(models.Model):
    '''竞赛题目'''
    problem_id = models.ForeignKey(Problem)
    contest_id = models.ForeignKey(Contest) 
    title = models.CharField(max_length=200,blank=False,null=False)
    num = models.IntegerField(blank=False,null=False)
class ContestproblemAdmin(admin.ModelAdmin):
    list_display = ('problem_id','contest_id','title','num')

admin.site.register(Contestproblem,ContestproblemAdmin)
