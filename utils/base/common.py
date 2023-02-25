import logging

import paramiko

logger = logging.getLogger('my_debug_logger')


def check_device_ssh_available(hostname: str, username: str, password: str, port: int) -> tuple:
    # 创建SSH客户端对象
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到服务器
        ssh.connect(hostname=hostname, username=username, password=password, port=port)
        # 执行一些简单的命令
        stdin, stdout, stderr = ssh.exec_command('echo "www"')
        # 检查命令输出
        output = stdout.read().decode('utf-8')
        # 关闭连接
        ssh.close()
        if output.strip() == 'www':
            return True, 'success'
        else:
            logger.debug(f'Error happen when check device is available: \n{stderr.read().decode("utf-8")}')
            return False, stderr.read().decode('utf-8')
    except Exception as err:
        logger.debug(f'Exception happen when check device is available: \n{err}')
        return False, str(err)


if __name__ == '__main__':
    result = check_device_ssh_available('192.168.124.16', 'www', '123456', 22)
    print(result)
