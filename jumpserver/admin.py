#coding=utf-8
from django.contrib import admin
from models import Host, BindUserToHost, Log, Auth_user
# Register your models here.

class ChoiceInline(admin.StackedInline):
    model = BindUserToHost
    extra = 0

class Auth_userAdmin(admin.ModelAdmin):
    list_display = ('username','get_users','reg_time','last_login')


class HostsAdmin(admin.ModelAdmin):
    list_display = ('hostname','ip','note')
    inlines = [ChoiceInline]


class BindUserToHostAdmin(admin.ModelAdmin):
    list_display = ('username','passwd','get_host_ip','get_users','note')
    filter_horizontal = ('auth_user',)


class LogsAdmin(admin.ModelAdmin):
    list_display = ('id','log_file_path','log_time_path','build_time')


admin.site.register(Auth_user,Auth_userAdmin)
admin.site.register(Host,HostsAdmin)
admin.site.register(BindUserToHost,BindUserToHostAdmin)
admin.site.register(Log,LogsAdmin)
