import psutil
from channels.generic.websocket import JsonWebsocketConsumer


class ServerPerformanceConsumer(JsonWebsocketConsumer):

    def receive_json(self, content, **kwargs):
        if content.get('action') == 'get-performance-data':
            # 获取服务器性能相关数据
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent()
            virtual_memory = psutil.virtual_memory()
            total_memory = eval(f'{(virtual_memory.total / 1024 / 1024 / 1024):.2f}')
            available_memory = eval(f'{(virtual_memory.available / 1024 / 1024 / 1024):.2f}')
            free_memory = eval(f'{(virtual_memory.free / 1024 / 1024 / 1024):.2f}')
            used_memory = eval(f'{((virtual_memory.total - virtual_memory.free) / 1024 / 1024 / 1024):.2f}')
            memory_percent = eval(
                f'{((virtual_memory.total - virtual_memory.available) / virtual_memory.total * 100):.2f}')
            disk_info = psutil.disk_usage('/')
            total_disk = eval(f'{disk_info.total / 1024 / 1024 / 1024:.2f}')
            used_disk = eval(f'{disk_info.used / 1024 / 1024 / 1024:.2f}')
            free_disk = eval(f'{disk_info.free / 1024 / 1024 / 1024:.2f}')
            disk_percent = disk_info.percent
            server_data = {
                'cpu': {'cpu_count': cpu_count, 'cpu_percent': cpu_percent},
                'memory': {
                    'total_memory': total_memory, 'available_memory': available_memory, 'free_memory': free_memory,
                    'used_memory': used_memory, 'memory_percent': memory_percent
                },
                'disk': {
                    'total_disk': total_disk, 'used_disk': used_disk, 'free_disk': free_disk,
                    'disk_percent': disk_percent
                }
            }
            self.send_json({"data": server_data})
