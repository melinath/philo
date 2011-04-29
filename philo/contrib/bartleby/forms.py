"""
The Bartleby forms center around a central object: the DatabaseForm, so called
because it is a form created based on database input.
"""


from django import forms
from django.core.exceptions import ValidationError
from django.db.models.fields import NOT_PROVIDED
from django.utils.datastructures import SortedDict
from formwizard.forms import SessionFormWizard


POST_KEY = 'is_%s_form'


class DatabaseForm(forms.Form):
	"Contains functionality specific to database-driven forms."
	def __init__(self, request, data=None, files=None, auto_id='id_%s', prefix=NOT_PROVIDED, initial=None, *args, **kwargs):
		self.request = request
		if prefix is NOT_PROVIDED:
			prefix = self.instance.key
		if self.instance.allow_changes and self.instance.cookie_key in request.COOKIES:
			from philo.contrib.bartleby.models import ResultRow
			try:
				row = ResultRow.objects.filter(**self.get_record_kwargs()).latest()
			except:
				pass
			else:
				initial = initial or {}
				initial.update(dict([(value.field.key, value.value) for value in row.values.all().select_related('field')]))
		super(DatabaseForm, self).__init__(data, files, auto_id, prefix, initial, *args, **kwargs)
	
	def clean(self):
		cleaned_data = super(DatabaseForm, self).clean()
		request, instance = self.request, self.instance
		
		if request.method != 'POST' or not cleaned_data[make_post_key(instance)]:
			raise ValidationError("The form must be posted.")
		
		if instance.login_required and not (hasattr(request, 'user') and request.user.is_authenticated()):
			# If login is required for the form, don't display the form for unauthenticated requests.
			raise ValidationError("You must be logged in to submit this form.")
		
		# If allow_changes is true, this should instead check historical versions of the row -
		# or should there be native support? A "modified x times" field? an attribute?
		if not instance.allow_changes and instance.max_submissions > 0:
			try:
				kwargs = self._get_record_kwargs()
			except KeyError:
				# Then the cookie wasn't in request.COOKIES
				# TODO: This is not how we should check if cookies are enabled...
				# perhaps have a "has_valid_record" method?
				raise ValidationError("Cookies must be enabled to use this form.")
			
			if instance.result_rows.filter(**kwargs).count() >= instance.max_submissions:
				raise ValidationError("You have already submitted this form as often as possible.")
		
		return cleaned_data
	
	def _get_record_kwargs(self):
		"Return the kwargs necessary to fetch all rows for this instance's request and form instance."
		if not hasattr(self, '_record_kwargs'):
			request, instance = self.request, self.instance
			Form = instance.__class__
			
			self._record_kwargs = {'form': instance}
			
			if instance.record == Form.USER_CHOICE and hasattr(request, 'user') and request.user.is_authenticated():
				self._record_kwargs['user'] = request.user
			elif (instance.record == Form.USER_CHOICE and hasattr(request, 'user')) or (instance.record == Form.IP_CHOICE and 'REMOTE_ADDR' in request.META):
				self._record_kwargs['ip_address'] = request.META['REMOTE_ADDR']
			else:
				# In all other cases, we have no way of knowing for sure whether someone's already posted
				# unless we use cookies.
				self._record_kwargs['cookie'] = request.COOKIES[instance.cookie_key]
		
		return self._record_kwargs
	record_kwargs = property(_get_record_kwargs)
	
	def process(self):
		"""Get and merge receiver response dictionaries to make a dictionary appropriate for an ajax response."""
		from philo.contrib.bartleby.signals import process_bartleby_form
		response_dict = {}
		responses = process_bartleby_form.send(sender=self.instance, form=self)
		for receiver, value in responses:
			response_dict.update(value or {})
		return response_dict


def make_post_key(form):
	return POST_KEY % form.key


def field_dict_from_instance(instance):
	return SortedDict([(field.key, field.formfield()) for field in instance.fields.order_by('order')])


def databaseform_factory(instance, form=DatabaseForm):
	attrs = field_dict_from_instance(instance)
	attrs.update({
		'instance': instance,
		make_post_key(instance): forms.BooleanField(widget=forms.HiddenInput, initial=True)
	})
	return forms.forms.DeclarativeFieldsMetaclass("%sForm" % str(instance.name.replace(' ', '')), (form,), attrs)


class DatabaseFormWizard(SessionFormWizard):
	def __init__(self, form_view, *args, **kwargs):
		self.form_view = form_view
		super(DatabaseFormWizard, self).__init__(*args, **kwargs)
	
	def done(self, request, storage, final_form_list, **kwargs):
		extra_context = kwargs.get('extra_context', {})
		return self.form_view.form_complete_page.render_to_response(request, extra_context=extra_context)
	
	def render(self, request, storage, form, **kwargs):
		return self.form_view.form_display_page.render_to_response(request, extra_context=self.get_template_context(request, storage, form))