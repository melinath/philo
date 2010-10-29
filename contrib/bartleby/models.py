from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from philo.models import register_value_model, Entity, Titled, Template, ForeignKeyValue, ManyToManyValue
from philo.models.fields import JSONField
from philo.contrib.bartleby.forms import databaseform_factory, POST_KEY


#BLANK_CHOICE_DASH = [('', '---------')]


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
	is_anonymous = models.BooleanField(default=False)
	
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
	
	class Meta:
		unique_together = ('key', 'form')


class FieldChoice(models.Model):
	"Define choices inline."
	field = models.ForeignKey(Field, related_name="choices")
	key = models.SlugField(max_length=20)
	verbose_name = models.CharField(max_length=50)
	order = models.PositiveSmallIntegerField()


class ResultRow(models.Model):
	form = models.ForeignKey(Form, related_name='result_rows')
	submitted = models.DateTimeField()
	user = models.ForeignKey(User, blank=True, null=True)
	# Log the user's IP address for anonymous form submissions.
	ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)


class FieldValue(models.Model):
	field = models.ForeignKey(Field)
	value = JSONField()
	row = models.ForeignKey(ResultRow)
	
	class Meta:
		unique_together = ('field', 'row',)
