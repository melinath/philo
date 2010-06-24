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
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


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
	
	Submit/Continue buttons are auto-generated.
	"""
	order = models.PositiveIntegerField()
	instance_type = models.ForeignKey(ContentType , editable=False)
	item_name = ''
	
	@property
	def instance(self):
		try:
			return self.instance_type.get_object_for_this_type(id=self.id)
		except:
			return None
	
	def save(self, force_insert=False, force_update=False):
		if not hasattr(self, 'instance_type_ptr'):
			self.instance_type = ContentType.objects.get_for_model(self.__class__)
		super(FormItem, self).save(force_insert, force_update)
	
	class Meta:
		abstract = True


class TitledFormItem(FormItem):
	title = models.CharField(max_length=75)
	help_text = models.CharField(max_length=125, blank=True)
	
	class Meta:
		abstract = True


class NonFieldItem(FormItem):
	form = models.ForeignKey(FormModel, related_name='items')
	pass


class PageBreak(NonFieldItem):
	item_name = 'Page Break'


class SectionTitle(NonFieldItem, TitledFormItem):
	item_name = 'Section Title'


class FieldItem(TitledFormItem):
	form = models.ForeignKey(FormModel, related_name='fields')
	required = models.BooleanField()
	key = models.SlugField(max_length=30)
	
	def formfield(self, form_class=forms.CharField, **kwargs):
		"""Returns a django.forms.Field instance according to this item's settings."""
		defaults = {'required': self.required, 'label': self.title, 'help_text': self.help_text}
		defaults.update(kwargs)
		return form_class(**defaults)
	
	class Meta:
		unique_together = ('key', 'form',)

class CharField(FieldItem):
	item_name = 'Text'
	
	def formfield(self, **kwargs):
		defaults = {'form_class': forms.CharField, 'max_length': 200}
		defaults.update(kwargs)
		return super(CharField, self).formfield(**defaults)
	
	class Meta:
		verbose_name = 'Text Input'
		verbose_name_plural = 'Text Inputs'


class TextField(FieldItem):
	item_name = 'Paragraph Text'
	
	def formfield(self, **kwargs):
		defaults = {'widget': forms.Textarea}
		defaults.update(kwargs)
		return super(TextField, self).formfield(**defaults)
	
	class Meta:
		verbose_name = 'Paragraph Text Input'
		verbose_name_plural = 'Paragraph Text Inputs'


CHOICE_TYPES = (
	('radio', 'Multiple Choice',),
	('checkbox', 'Checkboxes',),
	('select', 'Choose from a list',),
)


class ChoiceField(FieldItem):
	item_type = models.CharField(max_length=8, choices=CHOICE_TYPES, default='select')
	CHOICE_FIELDS = {
		'radio': {'form_class': forms.ChoiceField, 'widget': forms.RadioSelect},
		'checkbox': {'form_class': forms.MultipleChoiceField, 'widget': forms.CheckboxSelectMultiple},
	}
	default = {'form_class': forms.ChoiceField}
	
	@property
	def item_name(self):
		for k,v in CHOICE_TYPES:
			if k == item_type:
				return v
		return ''
	
	def formfield(self, **kwargs):
		defaults = self.CHOICE_FIELDS.get(self.item_type, self.default)
		defaults.update(kwargs)
		return super(ChoiceField, self).formfield(**defaults)


class ChoiceOption(models.Model):
	item = models.ForeignKey(ChoiceField, related_name='choices')
	name = models.CharField(max_length=100)
	key = models.SlugField(max_length=100)


class ResultRow(models.Model):
	form = models.ForeignKey(FormModel, related_name='rows')
	user = models.ForeignKey(User, blank=True, null=True)
	timestamp = models.DateTimeField()
	
	class Meta:
		unique_together = ('form', 'user', 'timestamp')


class FieldValue(models.Model):
	field = models.ForeignKey(FieldItem) # and through it, to the form.
	row = models.ForeignKey(ResultRow, related_name='values')
	value = models.TextField()