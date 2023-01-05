# @ProjectName: beer_server
# @FileName: custom_server_error_500_handler.py

from django.http import JsonResponse
from rest_framework import status


def server_error(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    data = {
        'code': 40000,
        'message': '服务器开小差了(500)',
        'data': None
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
