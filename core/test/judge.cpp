/*
* Copyright 2008 sempr <iamsempr@gmail.com>
*
* Refacted and modified by zhblue<newsclan@gmail.com>
* Bug report email newsclan@gmail.com
*
*
* This file is part of HUSTOJ.
*
* HUSTOJ is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* HUSTOJ is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with HUSTOJ. if not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <time.h>
#include <stdarg.h>
#include <ctype.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/signal.h>
//#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <mysql/mysql.h>
#include <assert.h>

#define STD_MB 1048576
#define STD_T_LIM 2
#define STD_F_LIM (STD_MB<<5)
#define STD_M_LIM (STD_MB<<7)
#define BUFFER_SIZE 512
char work_dir[] = "/home/zyz/core/test/";
int OJ_AC = 3;
int OJ_WA = 4;
int OJ_RE = 5;
int OJ_TLE = 6;
int OJ_MLE = 7;
int OJ_PE = 8;
int OJ_OLE = 9;
int ACflg = 0;

void run_solution(int & lang,int & time_lmt, int & usedtime,int & mem_lmt) {
        nice(19);
        chdir(work_dir);
        // open the files
        freopen("data.in", "r", stdin);
        freopen("user.out", "w", stdout);
        freopen("error.out", "w", stderr);
        // trace me
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        // run me
        //if (lang != 2)
         // chroot(work_dir);
        //while(setgid(1536)!=0) sleep(1);
        //while(setuid(1536)!=0) sleep(1);
        //while(setresuid(1536, 1536, 1536)!=0) sleep(1);
        // set the limit
        struct rlimit LIM; // time limit, file limit& memory limit
        // time limit

        LIM.rlim_cur = (time_lmt - usedtime / 1000) + 1;

        LIM.rlim_max = LIM.rlim_cur;
        //if(DEBUG) printf("LIM_CPU=%d",(int)(LIM.rlim_cur));
        setrlimit(RLIMIT_CPU, &LIM);
        alarm(0);
        alarm(time_lmt*10);
        // file limit
        LIM.rlim_max = STD_F_LIM + STD_MB;
        LIM.rlim_cur = STD_F_LIM;
        setrlimit(RLIMIT_FSIZE, &LIM);
        // proc limit
        switch(lang){
            case 2: //java
                LIM.rlim_cur=LIM.rlim_max=800;
                break;
            default:
                LIM.rlim_cur=LIM.rlim_max=1;
        }
        setrlimit(RLIMIT_NPROC, &LIM);
        // set the stack
        LIM.rlim_cur = STD_MB << 6;
        LIM.rlim_max = STD_MB << 6;
        setrlimit(RLIMIT_STACK, &LIM);
        // set the memory
        LIM.rlim_cur = STD_MB *mem_lmt/2*3;
        LIM.rlim_max = STD_MB *mem_lmt*2;
        if(lang<2) setrlimit(RLIMIT_AS, &LIM);
        switch (lang) {
            case 0:
            case 1:
                    execl("./Main", "./Main", (char *)NULL);
                    break;
            case 2:
                    execl("/usr/bin/java", "/usr/bin/java", "-Xms32m","-Xmx256m",
                                    "-Djava.security.manager",
                                    "-Djava.security.policy=./java.policy", "Main", (char *)NULL);
                    break;
        }
        exit(0);

}

long get_file_size(const char * filename) {
        struct stat f_stat;

        if (stat(filename, &f_stat) == -1) {
                return 0;
        }

        return (long) f_stat.st_size;
}

int get_proc_status(int pid, const char * mark) {
        FILE * pf;
        char fn[BUFFER_SIZE], buf[BUFFER_SIZE];
        int ret = 0;
        sprintf(fn, "/proc/%d/status", pid);
        pf = fopen(fn, "r");
        int m = strlen(mark);
        while (pf && fgets(buf, BUFFER_SIZE - 1, pf)) {

                buf[strlen(buf) - 1] = 0;
                if (strncmp(buf, mark, m) == 0) {
                        sscanf(buf + m + 1, "%d", &ret);
                }
        }
        if (pf)
                fclose(pf);
        return ret;
}

int get_page_fault_mem(struct rusage & ruse, pid_t & pidApp) {
        //java use pagefault
        int m_vmpeak, m_vmdata, m_minflt;
        m_minflt = ruse.ru_minflt * getpagesize();
        return m_minflt;
}

void watch_solution(pid_t pidApp, int & ACflg, int isspj,int lang,
            int & topmemory, int mem_lmt, int & usedtime, int time_lmt) {
        char userfile[]="user.out";
        char infile[]="data.in";
        char outfile[]="data.out";

        // parent
        int tempmemory;
        int status, sig, exitcode;
        struct user_regs_struct reg;
        struct rusage ruse;
        int sub = 0;
        while (1) {
                // check the usage

                wait4(pidApp, &status, 0, &ruse);


//jvm gc ask VM before need,so used kernel page fault times and page size
                if (lang == 2) {
                        tempmemory = get_page_fault_mem(ruse, pidApp);
                } else {//other use VmPeak
                        tempmemory = get_proc_status(pidApp, "VmPeak:") << 10;
                }
                if (tempmemory > topmemory)
                        topmemory = tempmemory;
                if (topmemory > mem_lmt * STD_MB) {
                        if (ACflg == OJ_AC)
                                ACflg = OJ_MLE;
                        ptrace(PTRACE_KILL, pidApp, NULL, NULL);
                        break;
                }
                  //sig = status >> 8;

                if (WIFEXITED(status))
                        break;
                if ((lang < 4 || lang == 9) && get_file_size("error.out")) {
                        ACflg = OJ_RE;
                        //addreinfo(solution_id);
                        ptrace(PTRACE_KILL, pidApp, NULL, NULL);
                        break;
                }

                if (!isspj && get_file_size(userfile) > get_file_size(outfile) * 2+1024) {
                        ACflg = OJ_OLE;
                        ptrace(PTRACE_KILL, pidApp, NULL, NULL);
                        break;
                }

                exitcode = WEXITSTATUS(status);
                /*exitcode == 5 waiting for next CPU allocation * ruby using system to run,exit 17 ok
* */
                if ((lang >= 2 && exitcode == 17) || exitcode == 0x05 || exitcode == 0)
                        //go on and on
                        ;
                else {
                        //psignal(exitcode, NULL);

                        if (ACflg == OJ_AC){
                                switch (exitcode) {
                                        case SIGCHLD:
                                        case SIGALRM:
                                            alarm(0);
                                        case SIGKILL:
                                        case SIGXCPU:
                                                ACflg = OJ_TLE;
                                                break;
                                        case SIGXFSZ:
                                                ACflg = OJ_OLE;
                                                break;
                                        default:
                                                ACflg = OJ_RE;
                                }
                                //print_runtimeerror(strsignal(exitcode));
                        }
                        ptrace(PTRACE_KILL, pidApp, NULL, NULL);

                        break;
                }
                if (WIFSIGNALED(status)) {
                       /* WIFSIGNALED: if the process is terminated by signal
*
* psignal(int sig, char *s)，like perror(char *s)，print out s, with error msg from system of sig
* sig = 5 means Trace/breakpoint trap
* sig = 11 means Segmentation fault
* sig = 25 means File size limit exceeded
*/
                        sig = WTERMSIG(status);
                        if (ACflg == OJ_AC){
                                switch (sig) {
                                case SIGCHLD:
                                case SIGALRM:
                                    alarm(0);
                                case SIGKILL:
                                case SIGXCPU:
                                        ACflg = OJ_TLE;
                                        break;
                                case SIGXFSZ:
                                        ACflg = OJ_OLE;
                                        break;

                                default:
                                        ACflg = OJ_RE;
                                }
                               // print_runtimeerror(strsignal(sig));
                        }
                        break;
                }
                /* comment from http://www.felix021.com/blog/read.php?1662

WIFSTOPPED: return true if the process is paused or stopped while ptrace is watching on it
WSTOPSIG: get the signal if it was stopped by signal
*/

                // check the system calls
                ptrace(PTRACE_GETREGS, pidApp, NULL, &reg);
                ptrace(PTRACE_SYSCALL, pidApp, NULL, NULL);
        }
        usedtime += (ruse.ru_utime.tv_sec * 1000 + ruse.ru_utime.tv_usec / 1000);
        usedtime += (ruse.ru_stime.tv_sec * 1000 + ruse.ru_stime.tv_usec / 1000);

        //clean_session(pidApp);
}

int main(int argc,char *argv[]){
    int usedtime=0,ACflg=3,topmemory=0;
    int lang = atoi(argv[1]);
    int time_lmt = atoi(argv[2]);
    int mem_lmt = atoi(argv[3]);
    chdir(work_dir);
    pid_t pidApp = fork();
    if (pidApp == 0) {
        run_solution(lang,time_lmt,usedtime, mem_lmt);
    } else {

        watch_solution(pidApp,ACflg, 0,lang,topmemory, mem_lmt, usedtime, time_lmt);
        FILE *fp = fopen("res.txt","w");
        fprintf(fp,"%d\n%d\n%d\n",ACflg,topmemory,usedtime);
        fclose(fp);
    }
    return 0;
}

