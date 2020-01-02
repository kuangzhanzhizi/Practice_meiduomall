from django import http
from django.shortcuts import render, redirect
from django.views import View
import re
from .models import User
from django.contrib.auth import login
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
from django.contrib.auth import authenticate
# Create your views here.



class RegisterView(View):
	def get(self, request):
		return render(request, 'register.html')

	def post(self, request):
		# 接收,POST方法获取表单参数
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		password2 = request.POST.get('cpwd')
		mobile = request.POST.get('phone')
		sms_code = request.POST.get('msg_code')
		allow = request.POST.get('allow')
		# 验证
		# 1.非空
		if not all([username, password, password2, mobile, sms_code, allow]):
			return http.HttpResponseForbidden('填写数据不完整')
		# 2.用户名格式校验, 以及查看是否有重复用户名
		if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
			return http.HttpResponseForbidden('用户名为5-20个字符')
		if User.objects.filter(username=username).count() > 0:
			return http.HttpResponseForbidden('用户名已经存在')
		# 验证密码
		if not re.match('^[0-9A-Za-z]{8,20}$', password):
			return http.HttpResponseForbidden('密码为8-20个字符')
		if password != password2:
			return http.HttpResponseForbidden('两个密码不一致')
		if not re.match('^1[345789]\d{9}$', mobile):
			return http.HttpResponseForbidden('手机号错误')
		# 验证手机号是否重复
		if User.objects.filter(mobile=mobile).count() > 0:
			return http.HttpResponseForbidden('手机号已经存在')
		# 短信验证码
		# 1.读取redis中的短信验证码
		redis_cli = get_redis_connection('sms_code')
		sms_code_redis = redis_cli.get(mobile)
		# 2.判断是否过期
		if sms_code_redis is None:
			return http.HttpResponseForbidden('短信验证码已经过期')
		# 3.立即删除redis中的短信验证码, 不能使用第二次
		redis_cli.delete(mobile)
		redis_cli.delete(mobile+'_flag')
		# 4.判断是否正确
		if sms_code_redis.decode() != sms_code:
			return http.HttpResponseForbidden('短信验证码错误')

		# 处理
		# 1.创建用户对象, 使用这个方法原因是密码需要加密
		user = User.objects.create_user(
			username=username,
			password=password,
			mobile=mobile
		)
		# 2.状态保持
		login(request, user)
		# 响应
		return redirect('/')


class UsernameCountView(View):
	def get(self, request, username):
		# 接收,验证:通过正则表达式在路由中提取
		# 处理判断用户名是否存在
		count = User.objects.filter(username=username).count()
		# 响应:提示是否存在
		return http.JsonResponse({
			'count': count,
			'code': RETCODE.OK,
			'errmsg': 'OK'
		})


class MobileCountView(View):
	def get(self, request, mobile):
		count = User.objects.filter(mobile=mobile).count()
		return http.JsonResponse({
			'count': count,
			'code': RETCODE.OK,
			'errmsg': 'OK'
		})


class LoginView(View):
	def get(self, request):
		return render(request, 'login.html')

	def post(self, request):
		"""
		user = User.objects.get(username=username)
		user.password == pwd == 加密(pwd) ==> user.check_password(pwd)

		:param request:
		:return:
		"""

		# 接收
		username = request.POST.get('username')
		pwd = request.POST.get('pwd')
		# 验证
		user = authenticate(request, username=username, password=pwd)
		# 处理
		if user is None:
			# 用户名或者密码错误
			return http.HttpResponseForbidden('用户名或者密码错误')
		else:
			# 用户名或者密码正确
			# 2.状态保持
			# 响应
			login(request, user)
			return redirect('/')
