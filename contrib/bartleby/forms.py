"""
The Bartleby forms center around a central object: the DBForm, so called
because it is a form created based on database input.
"""


from django.forms import BaseForm, widgets
from inspect import ismethod
from django.utils.datastructures import SortedDict


def get_db_fields(bases, attrs):
	"""
	Create a list of form field instances from the passed-in 'instance' attr,
	plus any fields in bases.
	"""
	if attrs['instance'] is not None:
		fields = [(model.instance.title, model.instance.formfield()) for model in attrs['instance'].items.all() if hasattr(model.instance, 'formfield') and ismethod(model.instance.formfield)]
	else:
		fields = []
	
	for base in bases[::-1]:
		if hasattr(base, 'base_fields'):
			fields = base.base_fields.items() + fields
	
	return SortedDict(fields)


class DBFormMetaclass(type):
	"""
	Metaclass that finds field definitions on a FormItem-like object and adds
	them to a form.
	"""
	def __new__(cls, name, bases, attrs):
		attrs['base_fields'] = get_db_fields(bases, attrs)
		new_class = super(DBFormMetaclass, cls).__new__(cls, name, bases, attrs)
		if 'media' not in attrs:
			new_class.media = widgets.media_property(new_class)
		return new_class


class BaseDBForm(BaseForm):
	pass


class DBForm(BaseDBForm):
	__metaclass__ = DBFormMetaclass
	instance = None