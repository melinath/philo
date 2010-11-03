from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from philo.models import register_value_model, Entity, Titled, Template, ForeignKeyValue, Page, ManyToManyAttribute
from philo.models.fields import JSONField
from philo.contrib.bartleby.forms import databaseform_factory, POST_KEY
import datetime


#BLANK_CHOICE_DASH = [('', '---------')]
USER_CHOICE = 'u'
IP_CHOICE = 'i'
NULL_CHOICE = 'n'
FORM_RECORD_CHOICES = (
	(USER_CHOICE, 'User/IP Address'),
	(IP_CHOICE, 'IP Address'),
	(NULL_CHOICE, 'Nothing')
)


class Form(Entity, Titled):
	"""
	This model controls form-wide options such as data storage. In other words,
	should the form have a title? Help text? Should data be stored in the database
	or emailed to a set of users?
	
	It is important not to think of this as a django form. It is much more along
	the lines of a google form.
	"""
	help_text = models.TextField(blank=True)
	
	email_template = models.ForeignKey(Template, blank=True, null=True)
	email_from = models.CharField(max_length=200, verbose_name=_("from"), default="noreply@%s" % Site.objects.get_current().domain, blank=True)
	email_users = models.ManyToManyField(User, blank=True, null=True)
	email_groups = models.ManyToManyField(Group, blank=True, null=True)
	save_to_database = models.BooleanField(default=True)
	
	record = models.CharField(max_length=1, choices=FORM_RECORD_CHOICES, default=USER_CHOICE)
	login_required = models.BooleanField(default=False)
	allow_changes = models.BooleanField(default=False, help_text="Submitters will change their most recent submission instead of creating a new one.")
	max_submissions = models.SmallIntegerField(default=1, validators=[MinValueValidator(0)], help_text="The maximum number of submissions allowed for a given user or IP Address. Set to 0 for unlimited.")
	
	foreignkeyvalue_set = generic.GenericRelation(ForeignKeyValue)
	
	# Could have a TextField containing a list of forms to use as base classes... or one form class
	# to use in place of databaseform
	
	@property
	def form(self):
		if not hasattr(self, '_form'):
			self._form = databaseform_factory(self)
		
		return self._form
	
	# cleaning like this doesn't work with the admin. the form saves m2m and fk later, so this is bypassed.
	#def clean(self):
	#	if self.pk and (self.email_users.count() or self.email_groups.count()) and not self.email_template:
	#		raise ValidationError('To send email, an email template must be provided.')
	
	def is_available(self, request):
		# Future: Allow custom validation scripts in a text field to run the request through and check.
		return True
	
	def was_posted(self, request):
		# Should this rely on a function imported from bartleby.forms so the code relying on POST_KEY is
		# centralized?
		if request.method == 'POST' and '%s-%s' % (self.slug, (POST_KEY % self.slug)) in request.POST:
			return True
		return False
	
	def get_cookie_key(self):
		if not hasattr(self, '_cookie_key'):
			self._cookie_key = sha_constructor(settings.SECRET_KEY + unicode(self.pk) + unicode(self.slug)).hexdigest()[::2]
		return self._cookie_key
	cookie_key = property(get_cookie_key)
	
	def get_cookie_value(self):
		return sha_constructor(settings.SECRET_KEY + unicode(self.pk) + unicode(self.slug) + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).hexdigest()[::2]
	
	def get_email_recipients(self):
		return User.objects.filter(models.Q(form_set=self) | models.Q(group_set__form_set=self))
	email_recipients = property(get_email_recipients)
	
	class Meta:
		ordering = ('id',)

register_value_model(Form)

"""
class FormItem(models.Model):
	"Model for no-data items." - not strictly necessary for now.
	pass
"""

class Field(models.Model):
	key = models.SlugField(max_length=100) # necessary for form generation.
	form = models.ForeignKey(Form, related_name='fields')
	order = models.PositiveSmallIntegerField()
	
	label = models.CharField(max_length=100)
	help_text = models.CharField(max_length=100, blank=True)
	required = models.BooleanField()
	multiple = models.BooleanField(help_text=_("Allow multiple lines in a text field or choices in a choice field."))
	
	def formfield(self):
		# Make sure to pass in validators.
		kwargs = {
			'label': self.label,
			'required': self.required,
			'help_text': self.help_text
		}
		
		if self.choices.count():
			if self.multiple:
				return forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, **kwargs)
			else:
				return forms.ChoiceField(widget=forms.RadioSelect, **kwargs)
		
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
	form = models.ForeignKey(Form, related_name='result_rows')
	submitted = models.DateTimeField()
	user = models.ForeignKey(User, blank=True, null=True)
	
	# Log the user's IP address for anonymous form submissions.
	ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)
	
	# If that's too creepy for us, log a hashed cookie key.
	cookie = models.CharField(max_length=20, blank=True)
	
	def __unicode__(self):
		if self.user:
			return "%s - %s - %s" % (self.user, self.form, self.submitted.strftime("%Y-%m-%d %H:%M:%S"))
		return "%s - %s - %s" % (self.ip_address, self.form, self.submitted.strftime("%Y-%m-%d %H:%M:%S"))
	
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
	
	class Meta:
		unique_together = ('field', 'row',)
		ordering = ['field__order']


class FormPage(Page):
	forms = ManyToManyAttribute(Form)
	
	class Meta:
		proxy = True
		app_label = 'philo'