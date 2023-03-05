# Generated by Django 3.2.18 on 2023-03-05 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_alter_taskresult_task_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskresult',
            name='worker_name',
        ),
        migrations.AddField(
            model_name='taskresult',
            name='log',
            field=models.TextField(blank=True, default='', help_text='任务执行的log', verbose_name='任务执行的log'),
        ),
    ]