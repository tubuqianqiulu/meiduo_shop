#coding:utf-8

# jinja2的虚拟环境
from jinja2 import Environment
# django的一些依赖
from django.contrib.staticfiles.storage import staticfiles_storage
# urls需要和jinja进行一些配置
from django.urls import reverse


def environment(**options):
    env = Environment(**options)  # 把一些配置文件添加进去
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse
    })
    return env
