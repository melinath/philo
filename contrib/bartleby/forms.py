"""
The Bartleby forms center around a central object: the DatabaseForm, so called
because it is a form created based on database input.
"""


from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models.fields import NOT_PROVIDED
from django.template import Context
import datetime


IS_FORM = 'is_%s_form'


class DatabaseForm(forms.Form):
	"Contains functionality specific to database-driven forms."
	def __init__(self, data=None, files=None, auto_id='id_%s', prefix=NOT_PROVIDED, *args, **kwargs):
		if prefix is NOT_PROVIDED:
			prefix = self.instance.slug
		self.fields[IS_FORM % self.instance.slug] = forms.BooleanField(widget=forms.HiddenInput, initial=True)
		super(DatabaseForm, self).__init__(data, files, auto_id, prefix, *args, **kwargs)
	
	def save(self, request):
		# Save the result row for this form, if that's called for, and email the results to anyone
		# slated to get an email.
		if not (self.instance.save_to_database or (self.email_template and (self.email_users.count() or self.email_groups.count()))):
			return
		
		fields = self.instance.fields.all()
		
		field_values = [(field, self.cleaned_data.get(field.key, None)) for field in fields]
		
		if self.instance.save_to_database:
			from philo.contrib.bartleby.models import ResultRow, FieldValue
			row = ResultRow(form=self.instance, submitted=datetime.datetime.now())
			if request.user.is_authenticated() and not self.instance.is_anonymous:
				row.user = request.user
			else:
				row.ip_address = request.META.get('REMOTE_ADDR', None)
			row.save()
			
			for field, val in field_values:
				value = FieldValue(field=field, row=row)
				value.value = val
				value.save()
		
		if self.email_template and (self.email_users.count() or self.email_groups.count()):
			users = User.objects.filter(form_set=self.instance, group_set__form_set=self.instance)
			to_emails = users.values_list('email', flat=True)
			from_email = self.instance.from_email
			subject = "[%s] Form Submission: %s" % (Site.objects.get_current().domain, self.instance.title)
			t = self.email_template.django_template
			
			c = {
				'data': field_values
			}
			if request.user.is_authenticated():
				c.update({'user': request.user, 'ip_address': None})
			else:
				c.update({'user': None, 'ip_address': request.META.get('REMOTE_ADDR', None)})
			
			msg = t.render(Context(c))
			
			send_mail(subject, msg, from_email, to_emails)


def field_dict_from_instance(instance):
	return SortedDict([(field.key, field.formfield()) for field in instance.fields.order_by('order')])


def databaseform_factory(instance, form=DatabaseForm):
	attrs = field_dict_from_instance(instance)
	attrs.update({
		'instance': instance,
	})
	return forms.forms.DeclarativeFieldsMetaclass("%sForm" % str(instance.title.replace(' ', '')), (form,), attrs)