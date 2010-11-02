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
from django.utils.datastructures import SortedDict
import datetime


POST_KEY = 'is_%s_form'


class DatabaseForm(forms.Form):
	"Contains functionality specific to database-driven forms."
	def __init__(self, request, data=None, files=None, auto_id='id_%s', prefix=NOT_PROVIDED, *args, **kwargs):
		self.request = request
		if prefix is NOT_PROVIDED:
			prefix = self.instance.slug
		super(DatabaseForm, self).__init__(data, files, auto_id, prefix, *args, **kwargs)
	
	def clean(self):
		cleaned_data = super(DatabaseForm, self).clean()
		from philo.contrib.bartleby.models import USER_CHOICE, IP_CHOICE
		request, instance = self.request, self.instance
		
		if request.method != 'POST':
			raise ValidationError("The form must be posted.")
		
		if instance.login_required and not (hasattr(request, 'user') and request.user.is_authenticated()):
			# If login is required for the form, don't display the form for unauthenticated requests.
			raise ValidationError("You must be logged in to submit this form.")
		
		if instance.max_submissions > 0:
			# If a user has already posted the maximum number of times, don't make the form available.
			
			if instance.record == USER_CHOICE and hasattr(request, 'user') and request.user.is_authenticated():
				kwargs = {'user': request.user}
			elif (instance.record == USER_CHOICE and hasattr(request, 'user')) or (instance.record == IP_CHOICE and 'REMOTE_ADDR' in request.META):
				kwargs = {'ip_address': request.META['REMOTE_ADDR']}
			else:
				# In all other cases, we have no way of knowing for sure whether someone's already posted
				# unless we use cookies.
				if instance.cookie_key not in request.COOKIES:
					raise ValidationError("Cookies must be enabled to use this form.")
				
				kwargs = {'cookie': request.COOKIES[instance.cookie_key]}
			
			# If allow_changes is true, this should instead check historical versions of the row -
			# or should there be native support? A "modified x times" field?
			if instance.result_rows.filter(**kwargs).count() >= instance.max_submissions:
				raise ValidationError("You have already submitted this form as often as possible.")
		
		return cleaned_data
	
	def save(self):
		# Save the result row for this form, if that's called for, and email the results to anyone
		# slated to get an email.
		if self.errors:
			raise ValueError("The form could not be processed because the data didn't validate.")
		
		request, instance = self.request, self.instance
		if not instance.save_to_database and not (instance.email_template and instance.email_recipients):
			return
		
		fields = instance.fields.all()
		field_values = [(field, self.cleaned_data.get(field.key, None)) for field in fields]
		
		if instance.save_to_database:
			from philo.contrib.bartleby.models import ResultRow, FieldValue, USER_CHOICE, IP_CHOICE
			row = ResultRow(form=instance, submitted=datetime.datetime.now())
			
			if instance.record == USER_CHOICE and hasattr(request, 'user') and request.user.is_authenticated():
				row.user = request.user
			elif (instance.record == USER_CHOICE and hasattr(request, 'user')) or (instance.record == IP_CHOICE and 'REMOTE_ADDR' in request.META):
				row.ip_address = request.META['REMOTE_ADDR']
			else:
				row.cookie = request.COOKIES[instance.cookie_key]
			
			row.save()
			
			for field, val in field_values:
				value = FieldValue(field=field, row=row)
				value.value = val
				value.save()
		
		if instance.email_template and instance.email_recipients:
			to_emails = instance.email_recipients.values_list('email', flat=True)
			from_email = instance.from_email
			subject = "[%s] Form Submission: %s" % (Site.objects.get_current().domain, instance.title)
			t = self.email_template.django_template
			
			c = {
				'data': field_values
			}
			
			if instance.record == USER_CHOICE and hasattr(request, 'user') and request.user.is_authenticated():
				c.update({'user': request.user})
			elif (instance.record == USER_CHOICE and hasattr(request, 'user')) or (instance.record == IP_CHOICE and 'REMOTE_ADDR' in request.META):
				c.update({'ip_address': request.META['REMOTE_ADDR']})
			else:
				c.update({'cookie': request.COOKIES[instance.cookie_key]})
			
			msg = t.render(Context(c))
			
			send_mail(subject, msg, from_email, to_emails)


def field_dict_from_instance(instance):
	return SortedDict([(field.key, field.formfield()) for field in instance.fields.order_by('order')])


def databaseform_factory(instance, form=DatabaseForm):
	attrs = field_dict_from_instance(instance)
	attrs.update({
		'instance': instance,
		POST_KEY % instance.slug: forms.BooleanField(widget=forms.HiddenInput, initial=True)
	})
	return forms.forms.DeclarativeFieldsMetaclass("%sForm" % str(instance.title.replace(' ', '')), (form,), attrs)