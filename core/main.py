# -*- coding: utf-8 -*-
from daemon import Daemon
import MySQLdb
import time,sys,os
from os.path import getsize
from subprocess import *
import resource
from signal import alarm,SIGCHLD,SIGALRM,SIGKILL,SIGXCPU,SIGXFSZ
oj_home = '/home/zyz/core/'

STD_MB = 1048576
STD_T_LIM = 2
STD_F_LIM = (STD_MB<<5)
STD_M_LIM = (STD_MB<<7)
java_time_bonus = 5
java_memory_bonus = 512
OJ_AC = 3
OJ_WA = 4
OJ_RE = 5
OJ_TLE = 6
OJ_MLE = 7
OJ_PE = 8
OJ_OLE = 9
ACflg = 0

def connection():
    conn = MySQLdb.connect(host="localhost", # your host, usually localhost
                    user="root", # your username
                    passwd="1234", # your password
                    db="djangodb")
    return conn
#定时扫描数据库
def watch_db(conn):
    os.chdir(oj_home)
    cur = conn.cursor()
    sql = "select solution_id,problem_id_id,user_id_id,language from judge_solution where result = 0 order by solution_id asc limit 1"
    param = ()
    cur.execute(sql,param)
    res = cur.fetchall()
    s_id = 0
    p_id = 0
    u_id = 0
    isspj = 0
    lang = 0
    time_lmt = 1
    mem_lmt = 128
    if len(res) == 1:
        s_id = res[0][0]
        p_id = res[0][1]
        u_id = res[0][2]
        lang = res[0][3]
        sql = "select source from judge_sourcecode where solution_id_id =%s"
        param = (s_id)
        cur.execute(sql,param)
        source = cur.fetchall()[0][0]
        sql = "select spj,time_limit,memory_limit from judge_problem where problem_id =%s"
        param = (p_id)
        cur.execute(sql,param)
        res = cur.fetchall()
        isspj = res[0][0]
        time_lmt = res[0][1]
        mem_lmt = res[0][2]
        if lang == 0:
            print >> open('test/Main.c','w'),source
        elif lang == 1:
            print >> open('test/Main.cpp','w'),source
        elif lang == 2:
            print >> open('test/Main.java','w'),source
        else :#其他语言暂不考虑
            pass
        return 1,s_id,p_id,isspj,lang,time_lmt,mem_lmt,u_id
    else :
        return 0,s_id,p_id,isspj,lang,time_lmt,mem_lmt,u_id

#编译模块
def compile(lang):
    '''
编译成功返回0
否则返回错误信息的长度
'''
    os.chdir(oj_home+'test/')
    #C
    CP_C = ["gcc", "Main.c", "-o", "Main", "-O2","-Wall", "-lm","--static", "-std=c99", "-DONLINE_JUDGE"]
    #C++
    CP_X = ["g++", "Main.cpp", "-o", "Main", "-O2", "-Wall","-lm", "--static", "-DONLINE_JUDGE"]
    #java
    CP_J = ["javac", "-J-Xms32m", "-J-Xmx256m", "Main.java"]
    
    #CPU
    resource.setrlimit(resource.RLIMIT_CPU,(600,600));
    #最多打开的文件数
    resource.setrlimit(resource.RLIMIT_FSIZE,(900*STD_MB,900*STD_MB));
    #进程总共可用的内存大小的最大值
    resource.setrlimit(resource.RLIMIT_AS,(STD_MB<<11,STD_MB<<11));
    if lang == 0:
        proc=Popen(CP_C,stderr=PIPE)
    elif lang == 1:
        proc=Popen(CP_X,stderr=PIPE)
    elif lang == 2:
        proc=Popen(CP_J,stderr=PIPE)
    else:
        proc = None
        pass
    proc.wait()#等待子进程结束
    status = proc.returncode#执行结果状态 0表示正常 1表示编译错误
    info = proc.stderr.readlines()#错误信息
    err = ''
    if info:
        for i in info:
            err += i
    return status,err;


def update_compile(conn,s_id,info):
    '''
将编译错误信息插入到数据库
'''
    cur = conn.cursor()
    sql = "update judge_solution set result = 2 where solution_id= %s;"
    param = (str(s_id))
    cur.execute(sql,param)
    conn.commit()
    sql = "set names utf8;"
    cur.execute(sql)
    sql = "insert into judge_compileinfo(solution_id_id,error) values(%s,%s);"
    param = (str(s_id),info)
    cur.execute(sql,param)
    conn.commit()

def update_runing(conn,s_id):
    '''
更改当前状态为runing
'''
    cur = conn.cursor()
    sql = "update judge_solution set result = 1 where solution_id= %s;"
    param = (str(s_id))
    cur.execute(sql,param)
    conn.commit()

def compare(dir,std_dir):
    out = open(dir,"r").read()
    std_out = open(std_dir,"r").read()
    if out == std_out:
        return OJ_AC
    len1 = len(out)
    len2 = len(std_out)
    i = 0
    j = 0
    while(i<len1 and j<len2):
        while i<len1 and (out[i]==' ' or out[i]=='\n' or out[i] =='\r'):
            i += 1
        while j<len2 and (std_out[j]==' ' or std_out[j]=='\n' or std_out[j] =='\r'):
            j += 1
        if i<len1 and j<len2 and (out[i]!=std_out[j]):
            return OJ_WA;
        elif i==len1:
            break
        elif j==len2:
            break
        else:
            i += 1
            j += 1
    while i<len1:
        if(out[i]!=' ' and out[i]!='\n' or out[i] !='\r'):
            return OJ_WA
    while j<len2:
        if(std_out[j]!=' ' and std_out[j]!='\n' or std_out[j] !='\r'):
            return OJ_WA
    return OJ_PE

def judge_solution(lang,isspj,time_lmt,mem_lmt,ACflg,topmemory,usedtime):
    if ACflg == OJ_AC and usedtime >time_lmt*1000:
        ACflg = OJ_TLE
    if topmemory > mem_lmt*STD_MB:
        ACflg = OJ_MLE
    if ACflg == OJ_AC:
        comp_res = ACflg
        if isspj:#spj judge
            pass
        else:
            outfile = "data.out"
            userfile = "user.out"
            comp_res = compare(userfile,outfile,)
        if comp_res == OJ_WA:
                ACflg = OJ_WA
        elif comp_res == OJ_PE:
            PEflg = OJ_PE
        ACflg = comp_res
        #jvm popup messages, if don't consider them will get miss-WrongAnswer
        if lang == 2 and ACflg!=OJ_AC:
            #compres = fix_java_mis_judge
            pass
    return ACflg,usedtime,topmemory

def update_result(conn,s_id,flag,usetime,usemem):
    '''
更改result状态为ACflg,usetime,usemem
'''
    cur = conn.cursor()
    sql = "update judge_solution set result = %s where solution_id= %s;"
    param = (str(flag),s_id)
    cur.execute(sql,param)
    sql = "update judge_solution set time = %s where solution_id= %s;"
    param = (int(usetime),s_id)
    cur.execute(sql,param)
    sql = "update judge_solution set memory = %s where solution_id= %s;"
    param = (usemem,s_id)
    cur.execute(sql,param)
    conn.commit()


def judge(lang,isspj,time_lmt,mem_lmt,p_id):
    '''
运行编译结果，并观察内存时间的
'''
    #将时间限制，内存限制，语言写入到info.txt中
    os.chdir(oj_home+'test/')
  
    os.system('cp ../data/%s/data.in ./' % (p_id))
    os.system('cp ../data/%s/data.out ./' % (p_id))
    
    if lang == 2:#java
        time_lmt = time_lmt + java_time_bonus
        mem_lmt = mem_lmt + java_memory_bonus
    
    if time_lmt > 300 or time_lmt < 1:
        time_lmt = 300
    if mem_lmt > 1024 or mem_lmt < 1:
        mem_lmt = 1024
    #初始化元素值
    ACflg = OJ_AC
    PEflg = 0
    isspj = 0
    topmemory = 0
    usedtime = 0
    os.system("./judge %s %s %s"%(lang,time_lmt,mem_lmt))
    fp = open("res.txt","r")
    ACflg = int(fp.readline())
    topmemory = int(fp.readline())
    usedtime = int(fp.readline())
    os.system('rm data.in')
    ACflg,usetime,usemem = judge_solution(lang,isspj,time_lmt,mem_lmt,ACflg,topmemory,usedtime)
    os.system('rm user.out')
    os.system('rm data.out')
    return ACflg,usedtime,usemem

def run():
    os.chdir(oj_home)
    while True:
        time.sleep(5)
        conn = connection()
        #定时扫描新记录，
        hasnew,s_id,p_id,isspj,lang,time_lmt,mem_lmt,u_id = watch_db(conn)
        if hasnew:
            #返回编译结果和错误信息
            com_res,com_info = compile(lang)
            #print com_res,com_info
            if com_res==0:# 编译成功
                update_runing(conn,s_id)
                judge_res,usetime,usemem=judge(lang,isspj,time_lmt,mem_lmt,p_id)
                print "%s %s %s %s %s" % (u_id,s_id,judge_res,usetime,usemem>>10)
                update_result(conn,s_id,judge_res,usetime,usemem>>10)
            else:
                #将编译错误信息写入数据库
                print "error!"
                update_compile(conn,s_id,com_info)
        else :
            #继续扫描
            pass

    
#重写daemon的run方法
class MyDaemon(Daemon):
    def _run(self):
        run()
   
#通过脚本
if __name__ == "__main__":
    daemon = MyDaemon(oj_home+'tmp.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
