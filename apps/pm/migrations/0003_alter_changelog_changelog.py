# Generated by Django 3.2.16 on 2023-02-20 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm', '0002_alter_userfile_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelog',
            name='changelog',
            field=models.JSONField(help_text='变更记录内容', verbose_name='变更记录内容'),
        ),
    ]
