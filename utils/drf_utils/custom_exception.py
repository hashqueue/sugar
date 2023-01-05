# -*- coding: utf-8 -*-
# @File    : custom_exception.py
# @Software: PyCharm
# @Description:
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    自定义异常，需要在settings.py文件中进行全局配置
    1.在视图中的APIView中使用时,需要在验证数据的时候传入raise_exception=True说明需要使用自定义异常
    2.ModelViewSet中已经使用了raise_exception=True,所以无需配置
    3. 历史处理方法
        response = exception_handler(exc, context)
        if response is not None:
            if 'detail' in response.data:
                response.data = {'code': 40000, 'message': response.data.get('detail'), 'data': None}
            else:
                response.data = {'code': 40000, 'message': response.data, 'data': None}
        return response
    """
    response = exception_handler(exc, context)
    if response is not None:
        # 字段校验错误处理
        if isinstance(exc, ValidationError):
            if isinstance(response.data, dict):
                # 取错误信息中的一组数据返回
                error_data = list(dict(response.data).items())[0]
                # 该组数据的key，对应模型中的某个字段
                error_key = error_data[0]
                # 该组数据的value，有可能是多个错误校验提示信息，这里只取第一条
                error_value = error_data[1][0]
                response.data['message'] = f"{error_key}: {error_value}"
                for key in dict(response.data).keys():
                    # 删除多余错误信息
                    if key != 'message':
                        response.data.pop(key)
                response.data['code'] = 40000
                response.data['data'] = None
            if isinstance(response.data, list):
                response.data = {'code': 40000, 'message': response.data[0], 'data': None}
            return response
        if 'detail' in response.data:
            response.data = {'code': 40000, 'message': response.data.get('detail'), 'data': None}
        else:
            # 未知错误
            response.data = {'code': 40000, 'message': str(response.data), 'data': None}
        return response
    return response
