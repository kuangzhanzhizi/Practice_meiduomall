from django.contrib.auth.backends import ModelBackend
import re
# 指定应用的导包路径为meiduo_mall/apps
from users.models import User


# 对原有的认证功能进行扩展
class MeiduoModelBackend(ModelBackend):
	def authenticate(self, request, username=None, password=None, **kwargs):
		# 变量username的值, 可以是用户名 ,也可以手机号, 需要判断, 在查询
		try:
			if re.match(r'^1[3-9]\d{9}$', username):
				user = User.objects.get(mobile=username)
			else:
				user = User.objects.get(username=username)
		except Exception as e:
			# 如果未查到数据 则返回None 用于保持一致
			return None
		# 判断密码对不对
		if user.check_password(password):
			return user
		else:
			return None