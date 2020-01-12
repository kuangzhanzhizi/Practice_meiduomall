from django.shortcuts import render
from django.views import View
from .models import AreaInfo
from django import http
from meiduo_mall.utils.response_code import RETCODE
from django.core.cache import cache
from . import constants
# Create your views here.


class AreaView(View):
	def get(self, request):
		area_id = request.GET.get('area_id')
		if area_id is None:
			# 先获取缓存,如果缓存中不存在,在查询mysql并缓存
			result = cache.get('province_list')
			if result is None:
				# 没有传递地区编号, 表示查询省列表 属性和规则用__分割
				province_list = AreaInfo.objects.filter(parent__isnull=True)
				# print(province_list)
				# 只返回地区对象的编号和名称不需要空的partent_id
				province_list2 = list()
				for province in province_list:
					province_list2.append({
						'id': province.id,
						'name': province.name
					})
				result = {
					'code': RETCODE.OK,
					'errmsg': 'OK',
					'province_list': province_list2
				}
				# 缓存这个查询数据
				cache.set('province_list', result, constants.AREA_CACHE_EXPIRES)
			return http.JsonResponse(result)
		else:
			# 有地区编号, 表示查询指定地区的子级地区列表
			try:
				area = AreaInfo.objects.get(pk=area_id)
			except:
				return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '地区编号无效'})
			# 获取指定地区的子级地区
			# select b.name,b.parent_id from tb_areas as a INNER JOIN tb_areas as b WHERE a.id=b.parent_id;,
			result = cache.get('area_' + area_id)
			if result is None:
				sub_list = area.subs.all()
				# 整理前端需要数据格式
				sub_list2 = list()
				for sub in sub_list:
					sub_list2.append({
						'id': sub.id,
						'name': sub.name
					})
				result = {'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': {'id': area.id, 'name': area.name, 'subs': sub_list2}}
				cache.set('area_' + area_id, result, constants.AREA_CACHE_EXPIRES)
				return http.JsonResponse(result)