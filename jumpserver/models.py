#coding=utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.

#授权用户
class Auth_user(models.Model):
    username = models.CharField(u'跳板机用户名',max_length=32)
    reg_time = models.DateTimeField(u'注册时间', auto_now_add=True)
    last_login = models.DateTimeField(u'最后登录时间',null=True,blank=True)

    def __unicode__(self):
        return u"跳板机用户名:%s" % (self.username)

    def get_users(self):
        return ','.join([g.get_host_ip()+'-'+g.username for g in self.bindusertohost_set.select_related()])
    get_users.short_description='IP-授权用户'

class Host(models.Model):
    hostname = models.CharField(max_length=32)
    ip = models.CharField(max_length=16)
    # auth_user = models.ManyToManyField("Auth_user",blank=True)
    note = models.CharField(max_length=256,blank=True,null=True)
    port = models.IntegerField(default=22)

    def __unicode__(self):
        return "IP地址:%s" % (self.ip)

class BindUserToHost(models.Model):
    host = models.ForeignKey("Host")
    username = models.CharField(u'用户名',max_length=32)
    passwd = models.CharField(u'密码',max_length=256)
    note = models.CharField(u'备注',max_length=256)
    auth_user = models.ManyToManyField("Auth_user", blank=True)


    def get_users(self):
        return ','.join([g.username for g in self.auth_user.select_related()])
    get_users.short_description = '有权限的用户'

    def get_host_ip(self):
        return self.host.ip
    get_host_ip.short_description = 'IP地址'

class Log(models.Model):
    log = models.OneToOneField('Auth_user')
    log_file_path = models.CharField(u'内容记录文件',max_length=256)
    log_tiime_path = models.CharField(u'时间记录文件',max_length=256)
    build_time = models.DateTimeField(u'创建时间', null=True, blank=True)