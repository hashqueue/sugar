import datetime

import paramiko
from task.models import TaskResult


def get_current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def update_task_log(task_uuid, new_append_log):
    log = TaskResult.objects.filter(task_uuid=task_uuid).values_list('log', flat=True).first()
    TaskResult.objects.filter(task_uuid=task_uuid).update(
        log=f'{log}{get_current_time()} -> {new_append_log}\n')


def exec_cmd(ssh_client: paramiko.SSHClient, cmd: str):
    stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=60)
    # 检查命令输出
    output = stdout.read().decode('utf-8')
    err_put = stderr.read().decode('utf-8')
    return output.strip(), err_put.strip()
