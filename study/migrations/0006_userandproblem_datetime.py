# Generated by Django 2.2.1 on 2019-06-09 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0005_remove_userandproblem_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='userandproblem',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, default='2019-05-01 10:22:23', verbose_name='创建时间'),
            preserve_default=False,
        ),
    ]
