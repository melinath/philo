import datetime

from django import forms
from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

from philo.models import register_value_model, Entity, Template, Page, MultiView
from philo.models.fields import JSONField
from philo.contrib.bartleby.forms import databaseform_factory, DatabaseFormWizard


#BLANK_CHOICE_DASH = [('', '---------')]


class Form(Entity):
	"""The :class:`Form` model represents a collection of field configurations, much like a django form, but stored in the database."""
	
	name = models.CharField(max_length=150)
	help_text = models.TextField(blank=True)
	
	# Could have a TextField containing a list of forms to use as base classes... or one form class
	# to use in place of databaseform
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('id',)

register_value_model(Form)

"""
class FormItem(models.Model):
	"Model for no-data items." - not strictly necessary for now.
	pass
"""

class Field(models.Model):
	key = models.SlugField(max_length=50, db_index=True) # necessary for form generation.
	form = models.ForeignKey(Form, related_name='fields')
	order = models.PositiveSmallIntegerField()
	
	label = models.CharField(max_length=255)
	help_text = models.CharField(max_length=255, blank=True)
	required = models.BooleanField()
	multiple = models.BooleanField(help_text=_("Allow multiple lines in a text field or choices in a choice field."))
	
	def formfield(self):
		# Make sure to pass in validators.
		kwargs = {
			'label': self.label,
			'required': self.required,
			'help_text': self.help_text
		}
		
		choices = self.choices.all()
		if choices:
			choices = [(choice.key, choice.verbose_name) for choice in choices]
			if self.multiple:
				return forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices, **kwargs)
			else:
				return forms.ChoiceField(widget=forms.RadioSelect, choices=choices, **kwargs)
		
		if self.multiple:
			return forms.CharField(widget=forms.Textarea, **kwargs)
		
		return forms.CharField(**kwargs)
	
	def __unicode__(self):
		return "%s - %s" % (self.label, self.form)
	
	class Meta:
		unique_together = ('key', 'form')
		ordering = ['order']


class FieldChoice(models.Model):
	"Define choices inline."
	field = models.ForeignKey(Field, related_name="choices")
	key = models.SlugField(max_length=20)
	verbose_name = models.CharField(max_length=50)
	order = models.PositiveSmallIntegerField()
	
	class Meta:
		ordering = ['order']


class ResultRow(models.Model):
	form_view = models.ForeignKey('FormView', related_name="result_rows")
	submitted = models.DateTimeField()
	user = models.ForeignKey(User, blank=True, null=True)
	
	# Log the user's IP address for anonymous form submissions.
	ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)
	
	# If that's too creepy for us, log a hashed cookie key.
	cookie = models.CharField(max_length=20, blank=True)
	
	@property
	def submitter(self):
		return self.user or self.ip_address or self.cookie
	
	def __unicode__(self):
		return "%s - %s - %s" % (self.submitter, self.form_view, self.submitted.strftime("%Y-%m-%d %H:%M:%S"))
	
	class Meta:
		ordering = ['-submitted']
		get_latest_by = 'submitted'


class FieldValue(models.Model):
	field = models.ForeignKey(Field)
	value = JSONField()
	row = models.ForeignKey(ResultRow, related_name='values')
	
	def clean(self):
		if self.field.form != self.row.form:
			raise ValidationError("That field and row are not related to the same form.")
	
	def __unicode__(self):
		return "%s - %s - %s" % (self.value, self.field.key, self.row)
	
	class Meta:
		unique_together = ('field', 'row',)
		ordering = ['field__order']


class FormView(MultiView):
	name = models.CharField(max_length=100)
	form_display_page = models.ForeignKey(Page, related_name='form_display_related')
	form_complete_page = models.ForeignKey(Page, related_name='form_complete_related')
	forms = models.ManyToManyField(Form, through='FormStep')
	
	# Result emailing settings.
	results_email_page = models.ForeignKey(Page, related_name='form_results_email_related', blank=True, null=True)
	try:
		results_email_sender_default = "noreply@%s" % Site.objects.get_current().domain
	except:
		results_email_sender_default = settings.SERVER_EMAIL
	results_email_sender = models.CharField(max_length=200, verbose_name=_("from"), default=results_email_sender_default, blank=True)
	email_users = models.ManyToManyField(User, blank=True, null=True)
	email_groups = models.ManyToManyField(Group, blank=True, null=True)
	
	#: Whether to save to the database
	save_to_database = models.BooleanField(default=True)
	
	# Submission settings
	USER_CHOICE = 'u'
	IP_CHOICE = 'i'
	NULL_CHOICE = 'n'
	RECORD_CHOICES = (
		(USER_CHOICE, 'User/IP Address'),
		(IP_CHOICE, 'IP Address'),
		(NULL_CHOICE, 'Nothing')
	)
	record = models.CharField(max_length=1, choices=RECORD_CHOICES, default=USER_CHOICE)
	login_required = models.BooleanField(default=False)
	allow_changes = models.BooleanField(default=False, help_text="Submitters will change their most recent submission instead of creating a new one.")
	max_submissions = models.SmallIntegerField(default=1, validators=[MinValueValidator(0)], help_text="The maximum number of submissions allowed for a given user or IP Address. Set to 0 for unlimited.")
	
	formwizard_class = DatabaseFormWizard
	
	def __unicode__(self):
		return self.name
	
	@property
	def urlpatterns(self):
		urlpatterns = patterns('',
			url(r'^$', self.form_view, name='form_view')
		)
		return urlpatterns
	
	def get_formwizard(self):
		form_list = [step.get_form() for step in self.steps.all()]
		return self.formwizard_class(self, form_list)
	
	def form_view(self, request, extra_context=None):
		if self.login_required and not (hasattr(request, 'user') and request.user.is_authenticated()):
			# Really, this ought to redirect the user to a login. Should FormView subclass something
			# out of waldo?
			raise PermissionDenied("You must be logged in to submit this form.")
		
		if not self.allow_changes and self.max_submissions > 0:
			try:
				kwargs = self._get_row_kwargs(request)
			except KeyError:
				# Then the cookie wasn't in request.COOKIES
				# TODO: This is not how we should check if cookies are enabled...
				# perhaps have a "has_valid_record" method?
				raise PermissionDenied("Cookies must be enabled to use this form.")
			
			if self.result_rows.filter(**kwargs).count() >= self.max_submissions:
				raise PermissionDenied("You have already submitted this form as often as possible.")
		
		formwizard = self.get_formwizard()
		context = extra_context or {}
		return formwizard(request, extra_context=context)
	
	def _get_email_recipients(self):
		if not hasattr(self, '_email_recipients'):
			self._email_recipients = User.objects.filter(models.Q(formview=self) | models.Q(groups__formview=self))
		return self._email_recipients
	
	def _get_cookie_key(self, request):
		return sha_constructor(settings.SECRET_KEY + unicode(self.pk) + unicode(request.META.get('REMOTE_ADDR', None))).hexdigest()[::2]
	
	def _get_cookie_value(self, request):
		return sha_constructor(settings.SECRET_KEY + unicode(self.pk) + unicode(request.META.get('REMOTE_ADDR', None)) + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).hexdigest()[::2]
	
	def _get_row_kwargs(self, request):
		if self.record == self.USER_CHOICE and hasattr(request, 'user') and request.user.is_authenticated():
			return {'user': request.user}
		elif (self.record == self.USER_CHOICE and hasattr(request, 'user')) or (self.record == self.IP_CHOICE and 'REMOTE_ADDR' in request.META):
			return {'ip_address': request.META['REMOTE_ADDR']}
		# In all other cases, we have no way of knowing for sure whether someone's already posted
		# unless we use cookies.
		return {'cookie': request.COOKIES[self._get_cookie_key()]}
	
	def handle_submission(self, request, cleaned_forms, **kwargs):
		row = self.record_submission(request, cleaned_forms)
		
		if self.results_email_page and self._get_email_recipients():
			self.email_results(request, row, cleaned_forms)
		
		context = self.get_context()
		context.update(kwargs.get('extra_context', {}))
		context.update({
			'row': row,
			'forms': cleaned_forms
		})
		return self.form_complete_page.render_to_response(request, extra_context=context)
	
	def email_results(self, request, row, cleaned_forms):
		to_emails = self._get_email_recipients().values_list('email', flat=True)
		from_email = self.results_email_sender
		subject = "[%s] Form Submission: %s" % (Site.objects.get_current().domain, self.name)
		page = self.results_email_page
		c = {
			'row': row,
			'forms': cleaned_forms,
		}
		msg = page.render_to_string(request=request, extra_context=c)
		send_mail(subject, msg, from_email, to_emails)
	
	def record_submission(self, request, cleaned_forms):
		row_kwargs = self._get_row_kwargs(request)
		row = self.result_rows.create(submitted=datetime.datetime.now(), **row_kwargs)
		
		if cleaned_forms and self.save_to_database:
			for form in cleaned_forms:
				for field in form.instance.fields.all():
					value = FieldValue(field=field, row=row)
					value.value = form.cleaned_data.get(field.key, None)
					value.save()
		return row


class FormStep(models.Model):
	form = models.ForeignKey(Form)
	multiview = models.ForeignKey(FormView, related_name='steps')
	order = models.PositiveIntegerField()
	name = models.SlugField(max_length=50, blank=True)
	
	def get_form(self):
		form = databaseform_factory(self.form)
		return self.name and (self.name, form) or form
	
	class Meta:
		unique_together = (('form', 'multiview'), ('order', 'name', 'multiview'))
		ordering = ('order',)