import datetime

from django import forms
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.utils.datastructures import SortedDict
from formwizard.forms import SessionFormWizard


def field_dict_from_instance(instance):
	return SortedDict([(field.key, field.formfield()) for field in instance.fields.order_by('order')])


def databaseform_factory(instance, form=forms.Form):
	attrs = field_dict_from_instance(instance)
	attrs.update({
		'instance': instance,
	})
	return forms.forms.DeclarativeFieldsMetaclass("%sForm" % str(instance.name.replace(' ', '')), (form,), attrs)


class DatabaseFormWizard(SessionFormWizard):
	def __init__(self, form_view, *args, **kwargs):
		self.form_view = form_view
		# Do I need to set kwargs['initial_list'] based on a result row?
		super(DatabaseFormWizard, self).__init__(*args, **kwargs)
	
	def done(self, request, storage, final_form_list, **kwargs):
		form_view = self.form_view
		if form_view.save_to_database:
			self.save_to_database(request, final_form_list)
		
		if form_view.email_template and form_view._get_email_recipients():
			self.email(request, final_form_list)
		
		extra_context = kwargs.get('extra_context', {})
		return self.form_view.form_complete_page.render_to_response(request, extra_context=extra_context)
	
	def render(self, request, storage, form, **kwargs):
		return self.form_view.form_display_page.render_to_response(request, extra_context=self.get_template_context(request, storage, form))
	
	def save_to_database(self, request, final_form_list):
		from philo.contrib.bartleby import FieldValue
		row_kwargs = self.form_view._get_row_kwargs(request)
		row = self.form_view.result_rows.create(submitted=datetime.datetime.now(), **row_kwargs)
		
		for form in final_form_list:
			for field in form.instance.fields.all():
				value = FieldValue(field=field, row=row)
				value.value = form.cleaned_data.get(field.key, None)
				value.save()
	
	def email(self, request, final_form_list):
		to_emails = self.form_view._get_email_recipients().values_list('email', flat=True)
		from_email = self.form_view.results_email_sender
		subject = "[%s] Form Submission: %s" % (Site.objects.get_current().domain, self.form_view.name)
		page = self.form_view.results_email_page
		c = {
			'forms': final_form_list,
		}
		msg = page.render_to_string(request=request, extra_context=c)
		send_mail(subject, msg, from_email, to_emails)