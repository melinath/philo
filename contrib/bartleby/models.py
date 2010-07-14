"""
An attempt to make a django-driven form app similar to Google Forms.
A form can have any number of items related to it (foreignkey).
It also needs to have a result set - but how? I can't dynamically add and remove
databases... the result set, the values, would need to be attached to the form
field model, but also to each other.

the form field model would have any number of values (foreignkey). 
the values would have a foreignkey to the form field model and s foreignkey to a
'dataset' model. dataset can be same as form... no.
Each 'dataset' model is essentially one table row. foreignkey to form.
"""

"""
Note that really, I want to have groups of forms that come together. Each 'page'
is really a separate form in a list of forms - which page you're on and the values
entered on each page should be controlled by a session. Perhaps have the 'page
break', but in the make_form method, return a list of forms for each 'page' - no.
Do it in the metaclass.
"""


from django.db import models
from django import forms
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from philo.contrib.bartleby.utils import PluginLimiter, SubclassPluginLimiter
from philo.contrib.bartleby.forms.plugins import PluginForeignKey


BLANK_CHOICE_DASH = [('', '---------')]


class FormModel(models.Model):
	"""
	Can I somehow subclass this off of forms? Take advantage of built-in features?
	or make a subclass of forms in a forms.py file that takes this instead of a
	model. That might make more sense.
	
	Title and help_text are features of google forms, but GF also renders the form
	as a page. Depending on how we end up using these forms, that might not be an
	appropriate way of looking at things - i.e. perhaps the help text and title
	are more a part of the content of the page than part of the actual form.
	
	Google also offers, for oberlin logins:
		1. Require oberlin.edu sign-in to view this form
		2. Automatically collect respondent's Oberlin College username
		3. Allow users to edit responses.
	
	This model should also control whether its values are saved to the database
	or immediately emailed (and if emailed, then to who?)
	"""
	title = models.CharField(max_length=100) # Is this necessary?
	help_text = models.TextField(blank=True) # necessary?
	email_users = models.ManyToManyField(User, blank=True, null=True)
	save_to_database = models.BooleanField()
	_form = None
	
	def __unicode__(self):
		return self.title
	
	def make_form(self):
		from philo.contrib.bartleby.forms import DBForm
		class GeneratedForm(DBForm):
			instance = self
		return GeneratedForm
	
	@property
	def form(self):
		if not self._form:
			self._form = self.make_form()
		
		return self._form


class FormItemPluginMount(models.Model.__metaclass__):
	def __init__(cls, name, bases, attrs):
		if not hasattr(cls, 'plugins'):
			cls.plugins = []
		elif hasattr(cls, 'plugin_name'):
			cls.plugins.append(cls)


class FormItem(models.Model):
	"""
	Generic parent class for every form item: fields, buttons, page breaks.
	Essentially, you have a list of choices. Google's options are:
	
	Questions:
		1. Text (input field)
		2. Paragraph Text (textarea)
		3. Multiple choice (vertical radio) -- 'go to page depending on answer'
		4. checkboxes
		5. Choose from a list (select box)
		6. Scale (auto-generated radio numbers)
		7. Grid (a bunch of items sharing radio buttons.)
		
	Other:
		1. Section title (title + help text/desc)
		2. Page break
	
	Submit/Continue buttons are auto-generated?
	"""
	__metaclass__ = FormItemPluginMount
	_form_relationship = generic.GenericRelation('ItemFormRelationship', content_type_field='item_content_type', object_id_field='item_object_id')
	
	@property
	def form_relationship(self):
		return self._form_relationship.all()[0]
	
	@property
	def form(self):
		return self.form_relationship.form
	
	class Meta:
		abstract = True


class TitledFormItem(FormItem):
	title = models.CharField(max_length=75)
	help_text = models.CharField(max_length=125, blank=True)
	
	def __unicode__(self):
		return self.title
	
	class Meta:
		abstract = True


class FieldItem(TitledFormItem):
	required = models.BooleanField()
	key = models.SlugField(max_length=30)
	values = generic.GenericRelation('FieldValue', content_type_field='field_content_type', object_id_field='field_object_id')

	def formfield(self, form_class=forms.CharField, **kwargs):
		"""Returns a django.forms.Field instance according to this item's settings."""
		defaults = {'required': self.required, 'label': self.title, 'help_text': self.help_text}
		defaults.update(kwargs)
		return form_class(**defaults)

	class Meta:
		unique_together = ('key', 'form',)
		abstract = True


class ChoiceField(FieldItem):
	options = generic.GenericRelation('ChoiceOption', content_type_field='field_content_type', object_id_field='field_object_id')
	
	@property
	def choices(self):
		return [(option.key, option.name) for option in self.options.all()]
	
	def formfield(self, **kwargs):
		defaults = self.defaults
		defaults.update(kwargs)
		return super(ChoiceField, self).formfield(**defaults)
	
	def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
		first_choice = include_blank and blank_choice or []
		return first_choice + list(self.choices)
	
	class Meta:
		abstract = True


_item_content_type_limiter = PluginLimiter(FormItem)
_field_content_type_limiter = SubclassPluginLimiter(FieldItem)
_choice_content_type_limiter = SubclassPluginLimiter(ChoiceField)


class PageBreak(FormItem):
	plugin_name = 'Page Break'


class SectionTitle(TitledFormItem):
	plugin_name = 'Section Title'

	class Meta:
		unique_together = ('key', 'form',)
		abstract = True


class CharField(FieldItem):
	plugin_name = 'Text'
	
	def formfield(self, **kwargs):
		defaults = {'form_class': forms.CharField, 'max_length': 200}
		defaults.update(kwargs)
		return super(CharField, self).formfield(**defaults)
	
	class Meta:
		verbose_name = 'Text Input'
		verbose_name_plural = 'Text Inputs'


class TextField(FieldItem):
	plugin_name = 'Paragraph Text'
	
	def formfield(self, **kwargs):
		defaults = {'widget': forms.Textarea}
		defaults.update(kwargs)
		return super(TextField, self).formfield(**defaults)
	
	class Meta:
		verbose_name = 'Paragraph Text Input'
		verbose_name_plural = 'Paragraph Text Inputs'


class RadioChoiceField(ChoiceField):
	plugin_name = 'Multiple Choice'
	defaults = {'form_class': forms.ChoiceField, 'widget': forms.RadioSelect}


class CheckboxChoiceField(ChoiceField):
	plugin_name = 'Checkboxes'
	defaults = {'form_class': forms.MultipleChoiceField, 'widget': forms.CheckboxSelectMultiple}


class SelectChoiceField(ChoiceField):
	plugin_name = 'Choose from a list'
	defaults = {'form_class': forms.ChoiceField}


class ChoiceOption(models.Model):
	field_content_type = models.ForeignKey(ContentType, limit_choices_to=_choice_content_type_limiter)
	field_object_id = models.PositiveIntegerField()
	field = generic.GenericForeignKey('field_content_type', 'field_object_id')
	name = models.CharField(max_length=100)
	key = models.SlugField(max_length=100)


class ResultRow(models.Model):
	form = models.ForeignKey(FormModel, related_name='rows')
	user = models.ForeignKey(User, blank=True, null=True)
	timestamp = models.DateTimeField()
	
	class Meta:
		unique_together = ('form', 'user', 'timestamp')


class FieldValue(models.Model):
	field_content_type = models.ForeignKey(ContentType, limit_choices_to=_field_content_type_limiter)
	field_object_id = models.PositiveIntegerField()
	field = generic.GenericForeignKey('field_content_type', 'field_object_id') # and through it, to the form.
	row = models.ForeignKey(ResultRow, related_name='values')
	value = models.TextField()


class ItemFormRelationship(models.Model):
	form = models.ForeignKey(FormModel, related_name='items')
	item_content_type = PluginForeignKey(ContentType, limit_choices_to=_item_content_type_limiter, verbose_name='Question type')
	item_object_id = models.PositiveIntegerField(blank=True, null=True, editable=False)
	item = generic.GenericForeignKey('item_content_type', 'item_object_id')
	creation_counter = models.PositiveIntegerField(verbose_name='order', editable=False)
	
	_item = None
	_item_content_type = None
	_item_object_id = None
	
	def __init__(self, *args, **kwargs):
		super(ItemFormRelationship, self).__init__(*args, **kwargs)
		
		# Cache for comparison later
		if self.item is not None:
			self._item = self.item
			self._item_content_type = self.item_content_type
			self._item_object_id = self.item_object_id
	
	def save(self):
		if self.pk is not None:
			if self._item != self.item and self._item is not None:
				self._item.delete()
		
		if self.creation_counter is None:
			max_creation_counter = self.form.items.filter(form=self.form).aggregate(max=models.Max('creation_counter'))['max'] or 0
			self.creation_counter = int(max_creation_counter) + 1
		
		super(ItemFormRelationship, self).save()
	
	def __unicode__(self):
		return '%s -> %s' % (self.form, self.item)
	
	class Meta:
		unique_together = ('item_content_type', 'item_object_id')
		ordering = ['creation_counter']
