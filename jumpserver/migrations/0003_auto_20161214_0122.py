# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-14 01:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jumpserver', '0002_auto_20161213_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u751f\u6210\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='auth_user',
            name='username',
            field=models.CharField(max_length=32, verbose_name='\u8df3\u677f\u673a\u7528\u6237\u540d'),
        ),
        migrations.AlterField(
            model_name='bindusertohost',
            name='note',
            field=models.CharField(max_length=256, verbose_name='\u5907\u6ce8'),
        ),
        migrations.AlterField(
            model_name='bindusertohost',
            name='passwd',
            field=models.CharField(max_length=256, verbose_name='\u5bc6\u7801'),
        ),
        migrations.AlterField(
            model_name='bindusertohost',
            name='username',
            field=models.CharField(max_length=32, verbose_name='\u7528\u6237\u540d'),
        ),
        migrations.AlterField(
            model_name='log',
            name='log_file_path',
            field=models.CharField(max_length=256, verbose_name='\u5185\u5bb9\u8bb0\u5f55\u6587\u4ef6'),
        ),
        migrations.AlterField(
            model_name='log',
            name='log_tiime_path',
            field=models.CharField(max_length=256, verbose_name='\u65f6\u95f4\u8bb0\u5f55\u6587\u4ef6'),
        ),
    ]
