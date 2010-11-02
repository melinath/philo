from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson as json
from django.utils.decorators import decorator_from_middleware
from philo.contrib.bartleby.utils import get_view_forms
from philo.exceptions import MIDDLEWARE_NOT_CONFIGURED


class BartlebyFormMiddleware(object):
	def process_view(self, request, view_func, view_args, view_kwargs):
		if not hasattr(request, 'node'):
			raise MIDDLEWARE_NOT_CONFIGURED # Raise a more explicit error?
		
		if not request.node:
			return
		
		forms = get_view_forms(request.node.view, request.node)
		
		if not forms:
			return
		
		django_forms = {}
		
		if request.method == 'POST':
			all_valid = True
			for form in forms:
				if form.is_available(request) and form.was_posted(request):
					form_instance = form.form(request, request.POST)
					django_forms[form.slug] = form_instance
				
					if not form_instance.is_valid():
						all_valid = False
			
			if all_valid:
				for form in django_forms.values():
					form.save()
				if request.is_ajax():
					# do something ajaxy - but what? maybe give the form a get_ajax_dict function and then
					# have an ajax_dict which gets updated from each form, then return a dump of the results.
					return HttpResponse(json.dumps({'errors': {}}))
				else:
					return HttpResponseRedirect('')
			elif request.is_ajax():
				errors = {}
				for form in django_forms.values():
					# This is fine because shared fields shouldn't be happening...
					errors.update(form.errors)
				return HttpResponse(json.dumps({'errors': errors}))
		
		for form in forms:
			if form.is_available(request) and (request.method != 'POST' or form.slug not in django_forms):
				django_forms[form.slug] = form.form(request)
		
		view_kwargs['forms'] = django_forms
		request._bartleby_forms = forms
	
	def process_response(self, request, response):
		if hasattr(request, '_bartleby_forms'):
			for form in request._bartleby_forms:
				if form.cookie_key not in request.COOKIES:
					response.set_cookie(form.cookie_key, value=form.get_cookie_value(), max_age=60*60*24*90)
		
		return response


form_decorator = decorator_from_middleware(BartlebyFormMiddleware)