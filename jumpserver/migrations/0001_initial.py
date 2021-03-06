# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auth_user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32)),
                ('reg_time', models.DateTimeField(auto_now_add=True, verbose_name='\u6ce8\u518c\u65f6\u95f4')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='\u6700\u540e\u767b\u5f55\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='BindUserToHost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32)),
                ('passwd', models.CharField(max_length=256)),
                ('note', models.CharField(max_length=256)),
                ('auth_user', models.ManyToManyField(blank=True, to='jumpserver.Auth_user')),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=32)),
                ('ip', models.CharField(max_length=16)),
                ('note', models.CharField(blank=True, max_length=256, null=True)),
                ('port', models.IntegerField(default=22)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_file_path', models.CharField(max_length=256)),
                ('log_tiime_path', models.CharField(max_length=256)),
                ('log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jumpserver.Auth_user')),
            ],
        ),
        migrations.AddField(
            model_name='bindusertohost',
            name='host',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jumpserver.Host'),
        ),
    ]
