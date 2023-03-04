# Generated by Django 3.2.18 on 2023-03-05 02:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskResult',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间')),
                ('creator', models.CharField(help_text='创建人', max_length=150, verbose_name='创建人')),
                ('modifier', models.CharField(help_text='最后修改人', max_length=150, verbose_name='最后修改人')),
                ('task_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='任务ID', primary_key=True, serialize=False, unique=True, verbose_name='任务ID')),
                ('task_status', models.PositiveSmallIntegerField(choices=[(0, 'PENDING'), (1, 'RECEIVED'), (2, 'STARTED'), (3, 'SUCCESS'), (4, 'FAILURE'), (5, 'REVOKED'), (6, 'RETRY'), (7, 'IGNORED'), (8, 'Queued')], default=0, help_text='任务状态', verbose_name='任务状态')),
                ('task_type', models.PositiveSmallIntegerField(choices=[(0, 'collect_device_perf_data')], default=0, help_text='任务类型', verbose_name='任务类型')),
                ('worker_name', models.CharField(blank=True, default='', help_text='执行任务的worker名称', max_length=100, verbose_name='执行任务的worker名称')),
                ('result', models.JSONField(default=None, help_text='任务执行结果', null=True, verbose_name='任务执行结果')),
                ('traceback', models.JSONField(blank=True, help_text='任务执行异常时的堆栈信息', null=True, verbose_name='Task Traceback')),
                ('metadata', models.JSONField(default=None, help_text='任务元数据信息(e.g. arguments, keyword arguments, etc.)', null=True, verbose_name='任务元数据信息')),
                ('device', models.ForeignKey(blank=True, help_text='所属设备', null=True, on_delete=django.db.models.deletion.SET_NULL, to='device.device', verbose_name='所属设备')),
            ],
            options={
                'verbose_name': '任务执行结果',
                'verbose_name_plural': '任务执行结果',
                'db_table': 'task_result',
            },
        ),
    ]
