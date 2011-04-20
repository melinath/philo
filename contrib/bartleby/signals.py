from philo.contrib.bartleby.models import ResultRow, FieldValue
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.dispatch import Signal
from django.template import Template, Context
import datetime


process_bartleby_form = Signal(providing_args=['form'])


def save_to_database(sender, form, **kwargs):
	if not (form.is_valid() and sender.save_to_database):
		return
	
	record_kwargs = form.record_kwargs
	cleaned_data = form.cleaned_data
	
	created = True
	
	if sender.allow_changes:
		try:
			row = ResultRow.objects.filter(**record_kwargs).latest()
			created = False
		except ResultRow.DoesNotExist:
			pass
	
	if created:
		row = ResultRow(**record_kwargs)
	
	row.submitted = datetime.datetime.now()
	row.save()
	
	for field in sender.fields.all():
		value = None
		if not created:
			try:
				value = FieldValue.objects.get(field=field, row=row)
			except FieldValue.DoesNotExist:
				pass
		
		if value is None:
			value = FieldValue(field=field, row=row)
		
		value.value = cleaned_data.get(field.key, None)
		value.save()
process_bartleby_form.connect(save_to_database)


def email(sender, form, **kwargs):
	if not (form.is_valid() and sender.email_template and sender.email_recipients):
		return
	
	to_emails = sender.email_recipients.values_list('email', flat=True)
	from_email = sender.email_from
	subject = "[%s] Form Submission: %s" % (Site.objects.get_current().domain, sender.name)
	t = Template(sender.email_template.code)
	
	fields = sender.fields.all()
	
	c = {
		'fields': dict([(field.key, field) for field in fields]),
		'data': dict([(field.key, form.cleaned_data.get(field.key, None)) for field in fields])
	}
	c.update(form.record_kwargs)
	msg = t.render(Context(c))
	send_mail(subject, msg, from_email, to_emails)
process_bartleby_form.connect(email)


def ajax_errors(sender, form, **kwargs):
	if form.is_valid() or not form.request.is_ajax():
		return
	
	return {
		'errors': form.errors
	}
process_bartleby_form.connect(ajax_errors)