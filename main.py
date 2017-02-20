#!/usr/bin/env python
#coding=utf-8
from my_ssh_client import SshTty
import getpass
import os, sys
import datetime
from log import logger
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Sylvanas.settings')
import django
django.setup()
from django.core.exceptions import ObjectDoesNotExist
from jumpserver.models import Auth_user,Host,Log

login_user = getpass.getuser()

def init_log(tty_log_dir,auth_user):
    # 记录用户的日志
    # tty_log_dir = os.path.join('/mylog/', 'ttylog')
    date_today = datetime.datetime.now()
    date_start = date_today.strftime('%Y%m%d')
    time_start = date_today.strftime('%H%M%S')
    today_connect_log_dir = os.path.join(tty_log_dir, date_start)
    log_file_path = os.path.join(today_connect_log_dir, '%s_%s' % (login_user, time_start))

    if not os.path.exists(today_connect_log_dir):
        try:
            os.makedirs(today_connect_log_dir)
            # os.popen('chmod 644 %s' % today_connect_log_dir)
        except Exception, e:
            logger.error('创建目录 %s 失败，请修改%s目录权限' % (today_connect_log_dir, tty_log_dir))
            print ('创建目录 %s 失败，请修改%s目录权限' % (today_connect_log_dir, tty_log_dir))
            os.sys.exit(-1)

    try:
        log_file = open(log_file_path + '.log', 'a')
        log_time = open(log_file_path + '.time', 'a')
        log_cmd  = open(log_file_path + '.cmd', 'a')
    except IOError:
        logger.debug('创建tty日志文件失败, 请修改目录%s权限' % today_connect_log_dir)
        print('创建tty日志文件失败, 请修改目录%s权限' % today_connect_log_dir)
        os.sys.exit(-1)
    log_obj = Log(
        log_id = auth_user.id,
        log_file_path = log_file_path + '.log',
        log_time_path = log_file_path + '.time',
        build_time = django.utils.timezone.now()
    )
    log_obj.save()

    log_file.write('Start at %s\r\n' % datetime.datetime.now())
    return log_file, log_time, log_cmd

def check_login():
    try:
        user = Auth_user.objects.get(username=login_user)
    except ObjectDoesNotExist:
        return False
    else:
        user.last_login = django.utils.timezone.now()
        user.save()
        return user


def get_input_num(maximum):
    while True:
        try:
            index = raw_input("\n\033[1;33m请输入对应数字:\033[0m")
        except (EOFError,KeyboardInterrupt):
            print("\033[1;31m\n无法退出堡垒机!\033[0m")
        else:
            if index.isdigit() and 0 < int(index) <= maximum :
                return int(index)
            else:
                print("\033[1;31m请输入1-%d之间的数字!\033[0m"%maximum)

def main():
    #验证用户是否存在
    auth_user = check_login()
    if not auth_user:
        print '你没有权限登录跳板机'
        os.sys.exit(-1)
    print '''\033[1;33m
    ##############################################

            ------欢迎登录堡垒机------
        上次登录时间:%s
    #############################################\033[0m
    '''%auth_user.last_login

    bindusertohost = auth_user.bindusertohost_set.select_related()

    if not bindusertohost:
        print '此用户没有授权可登录主机'
        os.sys.exit()

    #获取授权主机的IP列表
    hostname_list = [g.get_host_ip()+'   ' +g.get_host_note() for g in bindusertohost]
    #过滤相同的IP
    hostname_list = {}.fromkeys(hostname_list).keys()
    #打印授权主机列表
    for i in  range(len(hostname_list)):
        print '\033[1;32m %d-->   %s\033[0m'%(i+1,hostname_list[i])

    # 根据用户选择获取登录主机IP过滤授权的远程主机
    index = get_input_num(len(hostname_list))
    #获取远程主机IP
    remote_host_ip =  hostname_list[index-1].split('   ')[0]
    #根据ip地址获取和授权堡垒机用户获取远程主机(这是一个bindusertohost列表)
    auth_remote_user = auth_user.bindusertohost_set.filter(host__ip=remote_host_ip)
    #打印主机用户名列表
    if len(auth_remote_user)>1:
        print('请选择你要登录用户名')
        for i in  range(len(auth_remote_user)):
            print '\033[1;32m %d-->   %s\033[0m' % (i + 1, auth_remote_user[i].username)
        index = get_input_num(len(hostname_list))-1
    else:
        index=0

    obj = auth_remote_user[index]
    #获取host对象
    host_obj = Host.objects.get(ip=remote_host_ip)

    sshtty = SshTty(remote_host_ip, obj.username, obj.passwd,host_obj.port)
    log_file, log_time, log_cmd = init_log('/mylog/ttylog/',auth_user)
    sshtty.logging(log_file,log_time,log_cmd)
    sshtty.connect()

main()
# os.system("clear")
