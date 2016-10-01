# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-01 11:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20161001_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='childs',
            field=models.ManyToManyField(blank=True, to='app.User'),
        ),
        migrations.AlterField(
            model_name='user',
            name='expenses',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='app.Expense'),
        ),
        migrations.AlterField(
            model_name='user',
            name='master',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_master', to='app.User'),
        ),
    ]