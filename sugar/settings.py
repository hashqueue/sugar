"""
Django settings for sugar project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import sys
import environ
from datetime import timedelta
from pathlib import Path

env = environ.Env(DEBUG=(bool, False))
# Now `ENV_PATH=.env.prod ./manage.py runserver` uses `.env.prod` file while `./manage.py runserver` uses `.env` file.
env.read_env(env.str('ENV_PATH', '.env.dev'))
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加apps目录到python的里去
sys.path.insert(0, os.path.join(BASE_DIR, 'apps/'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
DEFAULT_USER_PASSWORD = env('DEFAULT_USER_PASSWORD')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ["*"]

# Application definition

# 设置自定义的用户模型类：被Django的认证系统所识别
AUTH_USER_MODEL = 'system.User'

INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',

    'system',
    'ws_server',
    'pm',
    'device'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'Sugar API',
    'DESCRIPTION': 'Sugar - 一站式项目研发管理平台接口文档',
    'VERSION': '1.0.0',
    'CONTACT': {"email": "1912315910@qq.com"},
    'LICENSE': {"name": "MIT License"},
    'SERVERS': [{"url": "http://127.0.0.1:8000"}],
}

API_VERSION = env('API_VERSION')
API_PREFIX = env('API_PREFIX')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 指定使用JWT认证
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 在全局指定分页的引擎
    'DEFAULT_PAGINATION_CLASS': 'utils.drf_utils.my_page_number_pagination.MyPageNumberPagination',
    # 同时必须指定每页显示的条数
    'PAGE_SIZE': 10,
    # 全局配置自定义异常
    'EXCEPTION_HANDLER': 'utils.drf_utils.custom_exception.custom_exception_handler',
    # 指定后端的schema为drf_spectacular的schema，用来生成接口文档
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES':
        [
            'rest_framework.permissions.IsAuthenticated',
            # 自定义rbac权限认证
            'utils.drf_utils.custom_permissions.RbacPermission',
        ],
    # 指定drf使用的过滤后端
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    # 接口限流
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '10000/day'
    },
    # API版本
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': API_VERSION,  # 默认的版本
    'ALLOWED_VERSIONS': [API_VERSION],  # 有效的版本
    'VERSION_PARAM': 'version',  # 版本的参数名与URL conf中一致
}

# djangorestframework-simplejwt配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    # 将refresh token的有效期改为2天
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}

# url权限认证白名单
WHITE_URL_LIST = [
    # 需要放开的接口权限[allow anyone which is authenticated]
    f'{API_PREFIX}/swagger/', f'{API_PREFIX}/redoc/', f'{API_PREFIX}/schema/', f'{API_PREFIX}/system/user/login/',
    f'{API_PREFIX}/system/user/token/refresh/', f'{API_PREFIX}/system/user/register/',
    rf'{API_PREFIX}/system/users/profile/', rf'{API_PREFIX}/system/users/reset-password/',
    rf'{API_PREFIX}/system/permissions/get-user-permissions/', rf'{API_PREFIX}/system/users/update-profile/'
]

AUTHENTICATION_BACKENDS = [
    # 自定义用户认证后端
    'utils.django_utils.custom_user_authentication_backend.MyCustomUserAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'sugar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'sugar.wsgi.application'
ASGI_APPLICATION = "sugar.asgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {'charset': 'utf8mb4'}
    }
}

# CACHES
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env('REDIS_CONNECT_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Celery配置选项
# 配置时区,使用与django项目相同的时区设置
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_ROUTES = {
    'device.tasks.check_device_is_alive': {'queue': 'check_device_alive', 'routing_key': 'check_device_alive'},
}
CELERY_TASK_QUEUES = {
    # queue name : { ...configs }
    'check_device_alive': {'exchange': 'sugar', 'exchange_type': 'direct', 'routing_key': 'check_device_alive'}
}

# 异步任务相关配置
TASK_CHECK_DEVICE_ALIVE_TIME = env('TASK_CHECK_DEVICE_ALIVE_TIME')
TASK_CHECK_DEVICE_ALIVE_RESULT_TIMEOUT = env('TASK_CHECK_DEVICE_ALIVE_RESULT_TIMEOUT')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
# 配置图片文件上传的存储路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# log
# 创建log文件的文件夹
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# django中的日志配置
LOGGING = {
    'version': 1,
    # 是否禁用已经存在的logger实例
    'disable_existing_loggers': False,
    # 日志显示格式
    'formatters': {
        # 简单格式
        'simple': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{',
        },
        # 详细格式
        'verbose': {
            'format': '{asctime} - {levelname} - {name} - [msg: {message}] - [{filename}: {lineno:d}]',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        # 只有debug=False且Error级别以上发邮件给admin
        "mail_admins": {
            "level": "ERROR",
            'filters': ['require_debug_false'],
            "class": "django.utils.log.AdminEmailHandler",
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'filters': ['require_debug_false'],
            'level': 'DEBUG',
            # 滚动生成日志，切割
            'class': 'logging.handlers.RotatingFileHandler',
            # 存放日志文件的位置
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8'
        },
    },
    'loggers': {
        # 自定义日志器 Usage
        # logger = logging.getLogger('my_debug_logger')
        # logger.debug(f'result: {build_result}')
        'my_debug_logger': {
            'handlers': ['console', 'file'],
            # 向不向更高级别的logger传递
            'propagate': True,
            # 日志器接收的最低日志级别
            'level': 'DEBUG'
        },
        # 记录与处理请求有关的信息. 5XX 的响应以 ERROR 消息的形式出现;4XX 的响应以 WARNING 消息的形式出现.
        'django.request': {
            'handlers': ['mail_admins', 'file', 'console'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
