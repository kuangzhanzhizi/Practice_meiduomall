from django.shortcuts import render
from django.views import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants
from django import http


class ImageCodeView(View):
	def get(self, request, uuid):
		# 接收
		# 验证
		# 处理
		# 1.生成图片文本、数据
		text, code, image = captcha.generate_captcha()
		# 2.保存图片文本,用户后续与用户输入值对比
		redis_cli = get_redis_connection('image_code')
		# setex设置过期时间(key,过期时间,value) 保存图片文本用于后续与用户的输入值对比
		redis_cli.setex(uuid, constants.IMAGE_CODE_EXPIRES, code)
		# 响应: 输出图片数据
		return http.HttpResponse(image, content_type='image/png')