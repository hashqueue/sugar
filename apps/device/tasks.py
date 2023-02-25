import datetime
import logging

import paramiko
from celery import Task as CTask, shared_task

from device.models import Device

logger = logging.getLogger('my_debug_logger')


class CheckDeviceStatusTask(CTask):

    def on_success(self, retval, task_id, args, kwargs):
        """

        @param retval: 任务函数返回的结果 e.g. {'result': True, 'msg': 'success, stdout is: www\n'}
        @param task_id: e2b0f61e-e25e-4d97-9881-41e9034b2007
        @param args: ['a', 1]
        @param kwargs: {'host': '192.168.124.16', 'username': 'ubuntu'}
        @return:
        """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """

        @param exc: 错误类型
        @param task_id:
        @param args:
        @param kwargs:
        @param einfo: 错误详细信息
        @return:
        """


@shared_task(base=CheckDeviceStatusTask)
def check_device_is_alive(host: str, username: str, password: str, port: int, device_id: int) -> dict:
    # 创建SSH客户端对象
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到服务器
        ssh.connect(hostname=host, username=username, password=password, port=port, timeout=60)
        # 执行一些简单的命令
        stdin, stdout, stderr = ssh.exec_command('echo "www"')
        # 检查命令输出
        output = stdout.read().decode('utf-8')
        # 关闭连接
        ssh.close()
        device = Device.objects.get(id=device_id)
        if output.strip() == 'www':
            # 将设备状态设置为在线
            if not device.device_status:
                Device.objects.filter(id=device_id).update(device_status=1, update_time=datetime.datetime.now())
            return {'result': True, 'msg': f'success, stdout is: {output}'}
        else:
            logger.error(f'Error happen when check device is available: \n{stderr.read().decode("utf-8")}')
            if device.device_status:
                Device.objects.filter(id=device_id).update(device_status=0, update_time=datetime.datetime.now())
            return {'result': False, 'msg': stderr.read().decode('utf-8')}
    except Exception as e:
        logger.exception(f'Exception happen when check device is available: \n{e}')
        device1 = Device.objects.get(id=device_id)
        if device1.device_status:
            Device.objects.filter(id=device_id).update(device_status=0, update_time=datetime.datetime.now())
        return {'result': True, 'msg': str(e)}
