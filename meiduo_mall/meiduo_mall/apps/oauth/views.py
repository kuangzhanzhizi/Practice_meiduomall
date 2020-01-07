from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.utils.response_code import RETCODE
from .models import OAuthQQUser
from meiduo_mall.utils import meiduo_signature
from . import contants
from users.models import User
# Create your views here.


class OAuthQQURLView(View):
	def get(self, request):
		# 创建授权对象
		oauthqq = OAuthQQ(
			settings.QQ_CLIENT_ID,
			settings.QQ_CLIENT_SECRET,
			settings.QQ_REDIRECT_URI,
			request.GET.get('next')
		)
		# 生成授权地址
		login_url = oauthqq.get_qq_url()
		# 响应
		return http.JsonResponse({
			'code': RETCODE.OK,
			'errmsg': 'OK',
			'login_url': login_url
		})


class OAuthQQOpenid(View):
	def get(self, request):
		code = request.GET.get('code')
		state = request.GET.get('state', '/')
		# 字典的两种写法
		# dict[key]
		# dict.get(key, '/')
		oauthqq = OAuthQQ(
			settings.QQ_CLIENT_ID,
			settings.QQ_CLIENT_SECRET,
			settings.QQ_REDIRECT_URI,
			state
		)
		# 1.根据code获取token
		token = oauthqq.get_access_token(code)
		# 2.根据token获取openid
		openid = oauthqq.get_open_id(token)
		# 判断是否是初次授权
		try:
			# 获取open_id的值
			qquser = OAuthQQUser.objects.get(openid=openid)
		except:
			# 将openid加密
			json_str = meiduo_signature.dumps({"openid": openid}, contants.OPENID_EXPIRES)
			# 显示绑定界面 返回给前端openid
			context = {
				'token': json_str
			}
			# 未查到数据,则为初次授权,显示绑定界面
			return render(request, 'oauth_callback.html', context)
		else:
			#查询到授权对象,则状态保持,转到相关页面 06:32
			# 根据外键user_id获取主键user对象
			user = qquser.user
			login(request, user)
			response = redirect(state)
			# 根据user对象查询username
			response.set_cookie('username', user.username)
			return response
		# return http.HttpResponse(openid)

	def post(self, request):
		# 接收:openid, mobile, password, sms_code
		access_token = request.POST.get('access_token')
		mobile = request.POST.get('mobile')
		pwd = request.POST.get('pwd')
		sms_code = request.POST.get('sms_code')
		state = request.GET.get('state', '/')
		print(access_token)
		# 验证:参考注册的验证, 解密
		openid_dict = meiduo_signature.loads(access_token, contants.OPENID_EXPIRES)
		if openid_dict is None:
			return http.HttpResponseForbidden('授权信息无效, 请重新授权')
		openid = openid_dict.get('openid')
		# 处理: 初次授权, 完成openid与user绑定
		# 1.判断手机号是否已经使用
		try:
			user = User.objects.get(mobile=mobile)
		except:
			# 2.如果未使用，则新建用户 create_user第一个就是用户名
			user = User.objects.create_user(mobile, password=pwd, mobile=mobile)
		else:
			# 3.如果已使用，则验证密码
			if not user.check_password(pwd):
				return http.HttpResponseForbidden('手机号已经使用')
		# 4 绑定:新建OAuthQQUser对象
		qquser = OAuthQQUser.objects.create(
			user=user,
			openid=openid
		)
		login(request, user)
		response = redirect(state)
		response.set_cookie('username', user.username)
		# 响应
		return response
