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
from jumpserver.models import Auth_user

def init_log():
    # 记录用户的日志

    tty_log_dir = os.path.join('/mylog/', 'ttylog')
    date_today = datetime.datetime.now()
    date_start = date_today.strftime('%Y%m%d')
    time_start = date_today.strftime('%H%M%S')
    today_connect_log_dir = os.path.join(tty_log_dir, date_start)
    log_file_path = os.path.join(today_connect_log_dir, '%s_%s_%s' % ('http', login_user, time_start))

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
    except IOError:
        logger.debug('创建tty日志文件失败, 请修改目录%s权限' % today_connect_log_dir)
        print('创建tty日志文件失败, 请修改目录%s权限' % today_connect_log_dir)
        os.sys.exit(-1)
    log_file.write('Start at %s\r\n' % datetime.datetime.now())
    return log_file, log_time

login_user = getpass.getuser()
try:
    user = Auth_user.objects.get(username=login_user)
except ObjectDoesNotExist:
    print '你没有权限登录跳板机'
    os.sys.exit(-1)
else:
    print '上次登录时间:%s'%user.last_login
    user.last_login = django.utils.timezone.now()
    user.save()


# sshtty = SshTty('183.129.171.34', 'http', 'xylx123',2222)
# log_file, log_time = init_log()
# sshtty.logging(log_file,log_time)
# sshtty.connect()