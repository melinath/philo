from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson as json
from django.utils.decorators import decorator_from_middleware
from philo.exceptions import MIDDLEWARE_NOT_CONFIGURED
from philo.models import Page
from philo.signals import view_about_to_render


def add_forms_to_context(sender, request, extra_context, **kwargs):
	if hasattr(request, '_bartleby_forms'):
		extra_context.update(request._bartleby_forms)
view_about_to_render.connect(add_forms_to_context)


class BartlebyFormMiddleware(object):
	def __init__(self, form_var='forms'):
		self.form_var = form_var
	
	def process_view(self, request, view_func, view_args, view_kwargs):
		if not hasattr(request, 'node'):
			raise MIDDLEWARE_NOT_CONFIGURED # Raise a more explicit error?
		
		if not request.node:
			return
		
		# For now, only enable this middleware for Pages.
		if not isinstance(request.node.view, Page):
			return
		
		forms = request.node.view.form_set.all()
		
		if not forms:
			return
		
		db_forms = {}
		if request.method == 'POST':
			ajax_response_dict = {}
			forms_to_process = []
			all_valid = True
			
			for form in forms:
				if form.was_posted(request):
					db_form = form.form(request, request.POST)
					
					if not db_form.is_valid():
						all_valid = False
					
					if db_form.has_changed():
						forms_to_process.append(db_form)
				else:
					db_form = form.form(request)
				
				db_forms[form.key] = db_form
			
			for db_form in forms_to_process:
				if all_valid or not db_form.is_valid():
					ajax_response_dict[db_form.prefix] = db_form.process()
			
			if forms_to_process:
				if request.is_ajax():
					return HttpResponse(json.dumps(ajax_response_dict))
				elif all_valid:
					return HttpResponseRedirect('')
		else:
			for form in forms:
				db_forms[form.key] = form.form(request)
		
		request._bartleby_forms = {self.form_var: db_forms}
	
	def process_response(self, request, response):
		if hasattr(request, '_bartleby_forms'):
			for db_form in request._bartleby_forms.get(self.form_var, {}).values():
				instance = db_form.instance
				if instance.cookie_key not in request.COOKIES:
					response.set_cookie(instance.cookie_key, value=instance.get_cookie_value(), max_age=60*60*24*90)
		
		return response


form_decorator = decorator_from_middleware(BartlebyFormMiddleware)