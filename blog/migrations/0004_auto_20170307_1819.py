# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_article_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='tag_name',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u6807\u7b7e\u540d\u79f0'),
        ),
    ]