from django.shortcuts import render
from django.views import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from . import constants
from django import http
from meiduo_mall.utils.response_code import RETCODE
import random
from meiduo_mall.libs.yuntongxun.sms import CCP


class ImageCodeView(View):
	def get(self, request, uuid):
		# 接收
		# 验证
		# 处理
		# 1.生成图片文本、数据
		text, code, image = captcha.generate_captcha()
		# 2.参数是cache中的键, 获得指定redis数据库的连接
		redis_cli = get_redis_connection('image_code')
		# setex设置过期时间(key,过期时间,value) 保存图片文本用于后续与用户的输入值对比
		redis_cli.setex(uuid, constants.IMAGE_CODE_EXPIRES, code)
		# 响应: 输出图片数据
		return http.HttpResponse(image, content_type='image/png')


class SmsCodeView(View):
	def get(self, request, mobile):
		# 接收 使用get的方法获取image_code_id的值
		uuid = request.GET.get('image_code_id')
		image_code = request.GET.get('image_code')
		# 验证
		# 1.非空
		if not all([uuid, image_code]):
			# 只要是ajax请求 都返回JsonResponse
			return http.JsonResponse({
				"code": RETCODE.PARAMERR,
				"errmsg": "参数不完整"
			})
		# 2.图形验证码是否正确
		# 2.1从redis中读取之前保存的图形验证码文本
		redis_cli = get_redis_connection('image_code')
		image_code_redis = redis_cli.get(uuid)
		# 2.2如果redis中的数据过期则提示
		if image_code_redis is None:
			return http.JsonResponse({
				"code": RETCODE.IMAGECODEERR,
				"errmsg": "图形验证码已过期,点击图片刷新"
			})
		# 立即删除redis中的图形验证码, 表示这个值不能使用第二次
		redis_cli.delete(uuid)
		# 对比图形验证码 不区分大小写 转换从redis读取的数据为bytes类型必须转换为string 不区分大小写
		if image_code_redis.decode().lower() != image_code.lower():
			return http.JsonResponse({
				"code": RETCODE.IMAGECODEERR,
				"errmsg": "图形验证码错误"
			})
		# 处理
		# 1.生成随机的6位数
		sms_code = '%06d' % random.randint(0, 999999)
		# 2.存入redis
		redis_cli = get_redis_connection('sms_code')
		redis_cli.setex(mobile, constants.SMS_CODE_EXPIERS, sms_code)
		# 3.发短信
		ccp = CCP()
		ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIERS/60], 1)
		print(sms_code)
		# 相应
		return http.JsonResponse({
			"code": RETCODE.OK,
			"errmsg": "OK"
		})