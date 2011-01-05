from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson as json
from django.utils.decorators import decorator_from_middleware
from philo.contrib.bartleby.utils import get_view_forms
from philo.exceptions import MIDDLEWARE_NOT_CONFIGURED
from philo.signals import view_about_to_render


def add_forms_to_context(sender, request, extra_context, **kwargs):
	if hasattr(request, '_bartleby_forms'):
		extra_context['forms'] = request._bartleby_forms
view_about_to_render.connect(add_forms_to_context)


class BartlebyFormMiddleware(object):
	def process_view(self, request, view_func, view_args, view_kwargs):
		if not hasattr(request, 'node'):
			raise MIDDLEWARE_NOT_CONFIGURED # Raise a more explicit error?
		
		if not request.node:
			return
		
		# XXX: Should forms really be inherited by views from nodes, anyway?
		forms = get_view_forms(request.node.view, request.node)
		
		if not forms:
			return
		
		db_forms = {}
		
		if request.method == 'POST':
			ajax_response_dict = {}
			
			for form in forms:
				all_valid = True
				if form.was_posted(request):
					db_form = form.form(request, request.POST)
					
					if not db_form.is_valid():
						all_valid = False
					
					if db_form.has_changed():
						ajax_response_dict[db_form.prefix] = db_form.process()
				else:
					db_form = form.form(request)
				
				db_forms[form.slug] = db_form
			
			if request.is_ajax():
				return HttpResponse(json.dumps(ajax_response_dict))
			elif all_valid:
				return HttpResponseRedirect('')
		else:
			for form in forms:
				db_forms[form.slug] = db_form
		
		request._bartleby_forms = db_forms
	
	def process_response(self, request, response):
		if hasattr(request, '_bartleby_forms'):
			for db_form in request._bartleby_forms:
				instance = db_form.instance
				if instance.cookie_key not in request.COOKIES:
					response.set_cookie(instance.cookie_key, value=instance.get_cookie_value(), max_age=60*60*24*90)
		
		return response


form_decorator = decorator_from_middleware(BartlebyFormMiddleware)