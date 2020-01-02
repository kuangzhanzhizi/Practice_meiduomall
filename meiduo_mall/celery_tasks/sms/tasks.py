from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants


# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@app.task(bind=True, name='send_sms', retry_backoff=3)
def send_sms(self, mobile, sms_code):
	# 将耗时的代码封装在一个方法中
	# ccp = CCP()
	# ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIERS], 1)
	print(sms_code)