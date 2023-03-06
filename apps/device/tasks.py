import datetime
import logging
import json
import os
import time
import traceback

import paramiko
from celery import Task as CTask, shared_task
from django.core.cache import cache

from device.models import Device
from task.models import TaskResult
from sugar.settings import TASK_CHECK_DEVICE_STATUS_RESULT_TIMEOUT, BASE_DIR, env
from utils.base.common import get_current_time, exec_cmd, update_task_log

logger = logging.getLogger('my_debug_logger')


class CheckDeviceStatusTask(CTask):

    def on_success(self, retval, task_id, args, kwargs):
        """

        @param retval: 任务函数返回的结果 e.g. {'result': True, 'msg': 'success, stdout is: ok\n'}
        @param task_id: Celery生成的task_id: e2b0f61e-e25e-4d97-9881-41e9034b2007, 非数据库中task_result表的task_uuid !!!
        @param args: ['a', 1]
        @param kwargs: {'host': '192.168.124.16', 'username': 'ubuntu'}
        @return:
        """
        kwargs.pop('password')
        device_id = kwargs.get('device_id')
        timestamp = datetime.datetime.timestamp(datetime.datetime.now())  # 1677398336.289207
        complete_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        val = {'task_id': task_id, 'task_status': 'success', 'args': args, 'kwargs': kwargs, 'error': None,
               'task_result': retval, 'complete_time': complete_time}
        cache.set(key=f'{device_id}_{timestamp}', value=json.dumps(val),
                  timeout=int(TASK_CHECK_DEVICE_STATUS_RESULT_TIMEOUT))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """

        @param exc: 错误类型
        @param task_id:
        @param args:
        @param kwargs:
        @param einfo: 错误详细信息
        @return:
        """
        kwargs.pop('password')
        device_id = kwargs.get('device_id')
        timestamp = datetime.datetime.timestamp(datetime.datetime.now())  # 1677398336.289207
        complete_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        val = {'task_id': task_id, 'task_status': 'failure', 'args': args, 'kwargs': kwargs, 'error': str(einfo),
               'task_result': None, 'complete_time': complete_time}
        cache.set(key=f'{device_id}_{timestamp}', value=json.dumps(val),
                  timeout=int(TASK_CHECK_DEVICE_STATUS_RESULT_TIMEOUT))


@shared_task(base=CheckDeviceStatusTask)
def check_device_status(host: str, username: str, password: str, port: int, device_id: int) -> dict:
    # 创建SSH客户端对象
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到服务器
        ssh.connect(hostname=host, username=username, password=password, port=port, timeout=10)
        # 执行一些简单的命令
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd='echo "ok"')
        # 关闭连接
        ssh.close()
        device = Device.objects.get(id=device_id)
        if stdout == 'ok':
            # 将设备状态设置为在线
            if not device.device_status:
                Device.objects.filter(id=device_id).update(device_status=1, update_time=datetime.datetime.now())
            return {'result': True, 'data': None, 'msg': stdout}
        else:
            logger.error(f'Error happened when check device is available: \n{stderr}')
            if device.device_status:
                Device.objects.filter(id=device_id).update(device_status=0, update_time=datetime.datetime.now())
            return {'result': False, 'data': None, 'msg': stderr}
    except Exception as e:
        logger.exception(f'Exception happened when check device is available: \n{e}')
        device1 = Device.objects.get(id=device_id)
        if device1.device_status:
            Device.objects.filter(id=device_id).update(device_status=0, update_time=datetime.datetime.now())
        return {'result': False, 'data': None, 'msg': f"{str(e)}, traceback:{traceback.format_exc()}"}


class DeployAgentToDeviceTask(CTask):
    def on_success(self, retval, task_id, args, kwargs):
        TaskResult.objects.filter(task_uuid=kwargs.get('task_uuid')).update(task_status=3,
                                                                            result={'data': retval,
                                                                                    'desc': retval.get('msg')})

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        TaskResult.objects.filter(task_uuid=kwargs.get('task_uuid')).update(task_status=4,
                                                                            result={'data': str(einfo),
                                                                                    'desc': 'not ok'},
                                                                            traceback=str(einfo))


@shared_task(base=DeployAgentToDeviceTask)
def deploy_agent_to_device(host: str, username: str, password: str, port: int, task_uuid: str) -> dict:
    time.sleep(5)  # 为了前端可以实时展示部署日志，这里睡眠5s
    # 创建SSH客户端对象
    ssh = paramiko.SSHClient()
    # 允许连接不在know_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接服务器
        ssh.connect(username=username, password=password, port=port, hostname=host, timeout=10)
        TaskResult.objects.filter(task_uuid=task_uuid).update(log=f'{get_current_time()} -> 连接服务器成功\n')

        # 获取内核架构成功
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd='arch')
        if stdout != '' and stderr == '':
            logger.info(f'Get kernelArch output: {stdout}')
            update_task_log(task_uuid, f'获取内核架构成功: kernelArch={stdout}')
        else:
            update_task_log(task_uuid, f'获取内核架构失败: {stderr}')
            return {'result': False, 'data': None, 'msg': f'获取内核架构失败: {stderr}'}

        sugar_agent_file_path = f"{os.path.join(BASE_DIR, 'static', 'media', 'agents')}"
        sugar_agent_file_name = 'sugar-agent_amd64'
        if stdout == 'x86_64':
            sugar_agent_file_path = os.path.join(sugar_agent_file_path, 'sugar-agent_amd64')
        elif stdout == 'aarch64':
            sugar_agent_file_path = os.path.join(sugar_agent_file_path, 'sugar-agent_arm64')
            sugar_agent_file_name = 'sugar-agent_arm64'
        update_task_log(task_uuid, f'将使用 {sugar_agent_file_name} 进行部署')

        # 获取$HOME的实际路径
        update_task_log(task_uuid, f'开始获取 $HOME 的实际路径')
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd='echo $HOME')
        if stdout != '' and stderr == '':
            home_file_path = stdout
            update_task_log(task_uuid, f'获取到 $HOME 的实际路径为{stdout}')
        else:
            update_task_log(task_uuid, f'获取 $HOME 的实际路径失败，失败原因：{stderr}')
            return {'result': False, 'data': None, 'msg': f'获取 $HOME 的实际路径失败，失败原因：{stderr}'}

        # 创建agent目录
        update_task_log(task_uuid, f'开始创建 {home_file_path}/sugar-agent 目录')
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd=f'mkdir -p {home_file_path}/sugar-agent')
        if stdout == '' and stderr == '':
            update_task_log(task_uuid, f'创建 {home_file_path}/sugar-agent 目录完成')
        else:
            update_task_log(task_uuid, f'创建 {home_file_path}/sugar-agent 目录完成失败，失败原因：{stderr}')
            return {'result': False, 'data': None,
                    'msg': f'创建 {home_file_path}/sugar-agent 目录完成失败，失败原因：{stderr}'}

        # 杀死已经存在的agent进程
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd=f"ps -ef | grep {sugar_agent_file_name} | grep -v grep | "
                                                      f"awk \'{{print $2}}\' | xargs kill -9")
        update_task_log(task_uuid, f'xargs kill -9 => stdout: {stdout}, stderr: {stderr}')
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd=f'killall {sugar_agent_file_name}')
        update_task_log(task_uuid, f'killall => stdout: {stdout}, stderr: {stderr}')
        time.sleep(3)

        # 上传agent文件
        sftp = ssh.open_sftp()
        update_task_log(task_uuid, f'开始上传 {sugar_agent_file_name} 文件')
        sftp.put(sugar_agent_file_path, f'{home_file_path}/sugar-agent/{sugar_agent_file_name}')
        update_task_log(task_uuid, f'上传 {sugar_agent_file_name} 文件完毕')

        update_task_log(task_uuid, f'开始启动 agent')
        # 启动agent
        # -host 192.168.124.12
        stdout, stderr = exec_cmd(ssh_client=ssh, cmd=f'nohup bash -c "cd {home_file_path}/sugar-agent/ && chmod u+x '
                                                      f'{sugar_agent_file_name} && ./{sugar_agent_file_name} '
                                                      f'-user {env("RABBITMQ_USER")} -password '
                                                      f'{env("RABBITMQ_PASSWORD")} -host {env("RABBITMQ_HOST")} -port '
                                                      f'{env("RABBITMQ_PORT")} -exchange-name device_exchange '
                                                      f'-queue-name collect_device_perf_data_queue -routing-key '
                                                      f'device_perf_data" > {home_file_path}/sugar-agent/agent.log'
                                                      f' 2>&1 &')
        if stderr == '':
            time.sleep(5)
            stdout, stderr = exec_cmd(ssh_client=ssh, cmd=f'cat {home_file_path}/sugar-agent/agent.log')
            if stderr == '' and 'Started consumer' in stdout and 'Waiting for messages' in stdout:
                update_task_log(task_uuid, f'启动 agent 成功\n{stdout}')
            else:
                update_task_log(task_uuid, f'启动 agent 失败，失败原因：{stdout}')
                return {'result': False, 'data': None, 'msg': f'启动 agent 失败，失败原因：{stdout}'}
        else:
            update_task_log(task_uuid, f'启动 agent 失败，失败原因：{stderr}')
            return {'result': False, 'data': None, 'msg': f'启动 agent 失败，失败原因：{stderr}'}
        sftp.close()
        ssh.close()
        return {'result': True, 'data': None, 'msg': "ok"}
    except Exception as e:
        logger.exception(f'Exception happened when deploy agent to device: \n{e}')
        update_task_log(task_uuid, f'Exception happened when deploy agent to device: \n{e}')
        return {'result': False, 'data': None, 'msg': f"{str(e)}, traceback:{traceback.format_exc()}"}
