from django.db import models

# Create your models here.


class AreaInfo(models.Model):
	name = models.CharField(max_length=20)
	# 如果需要关联别的表使用'应用.模型类',self 表示自关联(允许为空) 这个外键关联的是本表的主键
	# related_name 等于别名 从a.b_set b_set是a在定义外键时的隐藏属性===>a.subs 一对多
	parent = models.ForeignKey('self', null=True, blank=True, related_name='subs')
	# django框架根据外键parent自动创建"parent_id, parent_id代表主键

	class Meta:
		db_table = 'tb_areas'
		verbose_name = '省市区'
		verbose_name_plural = '省市区'

	def __str__(self):
		return self.name