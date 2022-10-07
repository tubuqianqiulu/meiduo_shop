from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import random
import logging
from meiduo_shop.libs.yuntongxun.sms import CCP
from verifications import constants

logger = logging.getLogger('django')  # 获取日志输入出器


class SMSCodeView(APIView):
    """发送短信验证码"""

    def get(self, request, mobile):
        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_codes')

        # 60秒内不允许重发发送短信
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({"message": "发送短信过于频繁"}, status=status.HTTP_400_BAD_REQUEST)

        # 生成和发送短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.debug(sms_code)

        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)

        # 以下代码演示redis管道pipeline的使用
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行
        pl.execute()

        # 响应发送短信验证码结果
        return Response({"message": "OK"})
