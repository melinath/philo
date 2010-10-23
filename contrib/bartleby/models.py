from django import forms
from django.contrib.auth.models import User, Group
from django.db import models
from philo.models.fields import JSONField
from philo.contrib.bartleby.forms import databaseform_factory


#BLANK_CHOICE_DASH = [('', '---------')]


class Form(models.Model):
	"""
	This model controls form-wide options such as data storage. In other words,
	should the form have a title? Help text? Should data be stored in the database
	or emailed to a set of users?
	
	It is important not to think of this as a django form. It is much more along
	the lines of a google form.
	"""
	title = models.CharField(max_length=100)
	help_text = models.TextField(blank=True)
	email_users = models.ManyToManyField(User, blank=True, null=True)
	email_groups = models.ManyToManyField(Group, blank=True, null=True)
	save_to_database = models.BooleanField(default=True)
	_form = None
	
	def __unicode__(self):
		return self.title
	
	@property
	def form(self):
		if not self._form:
			self._form = databaseform_factory(self)
		
		return self._form

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
	multiple = models.BooleanField(help_text="Allow multiple lines in a text field or choices in a choice field.")
	
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


class FieldChoice(models.Model):
	"Define choices inline."
	field = models.ForeignKey(Field, related_name="choices")
	key = models.SlugField(max_length=20)
	verbose_name = models.CharField(max_length=50)


class ResultRow(models.Model):
	form = models.ForeignKey(Form, related_name='result_rows')
	submitted = models.DateTimeField()
	user = models.ForeignKey(User, blank=True, null=True) # necessary?


class FieldValue(models.Model):
	field = models.ForeignKey(Field)
	value = JSONField()
	row = models.ForeignKey(ResultRow)
	
	class Meta:
		unique_together = ('field', 'row',)
