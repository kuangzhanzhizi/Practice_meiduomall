from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from meiduo_mall.utils.models import BaseModel
from areas.models import AreaInfo


class User(AbstractUser):
	mobile = models.CharField(max_length=11)
	email_active = models.BooleanField(default=False)
	#默认收获地址
	default_address = models.ForeignKey('users.Address', null=True, related_name='users')


class Address(BaseModel):
	# 关联用户
	user = models.ForeignKey(User, related_name='addresses')
	# 标题
	title = models.CharField(max_length=10, null=True)
	# 收件人
	receiver = models.CharField(max_length=10)
	# 省
	province = models.ForeignKey(AreaInfo, related_name='provinces')
	# 市
	city = models.ForeignKey(AreaInfo, related_name='citys')
	# 区县
	district = models.ForeignKey(AreaInfo, related_name='districts')
	# 详细地址
	detail_address = models.CharField(max_length=100)
	# 手机号
	mobile = models.CharField(max_length=11)
	# 固定电话
	phone = models.CharField(max_length=20)
	# 邮箱
	email = models.CharField(max_length=50)
	# 逻辑删除 逻辑删除本质 就是一个修改
	is_delete = models.BooleanField(default=False)

	class Meta:
		db_table = 'tb_addresses'
		# 根据修改时间 降序排列 继承制BaseModel
		ordering = ['-update_time']