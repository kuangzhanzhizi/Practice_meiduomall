from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
	@classmethod
	def as_view(cls, **kwargs):
		view = super().as_view(**kwargs)
		return login_required(view)