"""
The Bartleby forms center around a central object: the DBForm, so called
because it is a form created based on database input.
"""


from django.forms import BaseForm, widgets
from inspect import ismethod
from django.utils.datastructures import SortedDict
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from django.forms.util import ErrorList


def get_db_fields(bases, attrs):
	"""
	Create a list of form field instances from the passed-in 'instance' attr,
	plus any fields in bases.
	"""
	# prevent circular import.
	from philo.contrib.bartleby.models import FieldItem
	
	fields = []
	items = []
	if attrs['instance'] is not None:
		for rel in attrs['instance'].items.order_by('creation_counter'):
			item = rel.item
			if item is None:
				continue
			
			if isinstance(item, FieldItem):
				fields.append((item.key, item.formfield()))
			
			items.append(item)
	
	for base in bases[::-1]:
		if hasattr(base, 'base_fields'):
			fields = base.base_fields.items() + fields
	
	return (SortedDict(fields), items,)


class DBFormMetaclass(type):
	"""
	Metaclass that finds field definitions on a FormModel-like object and adds
	them to a form.
	"""
	def __new__(cls, name, bases, attrs):
		attrs['base_fields'], attrs['base_items'] = get_db_fields(bases, attrs)
		new_class = super(DBFormMetaclass, cls).__new__(cls, name, bases, attrs)
		if 'media' not in attrs:
			new_class.media = widgets.media_property(new_class)
		return new_class


class BaseDBForm(BaseForm):
	def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=':', empty_permitted=False, timestamp=None, user=AnonymousUser()):
		if user == AnonymousUser():
			user = None
		
		object_data = {}
		if timestamp:
			try:
				from philo.contrib.bartleby.models import ResultRow
				row = ResultRow.objects.get(form=self.instance, user=user, timestamp=timestamp)
				object_data.update(dict((value.field.key, value.value) for value in row.values.all()))
			except ResultRow.DoesNotExist:
				pass
		
		if initial is not None:
			object_data.update(initial)
		
		super(BaseDBForm, self).__init__(data, files, auto_id, prefix, object_data, error_class, label_suffix, empty_permitted)
				
	
	def save_to_db(self, user=AnonymousUser(), timestamp=datetime.now()):
		if not self.is_valid():
			raise Exception # what kind should I be raising?
		
		if self.instance == None:
			raise TypeError('None object is not a valid instance.')
		
		if user.is_anonymous():
			user = None
		
		form = self.instance
		row, created = form.rows.get_or_create(user=user, timestamp=timestamp)
		for field in form.fields.all():
			value, created = row.values.get_or_create(field=field)
			value.value = self.cleaned_data[field.key]
			value.save()


class DBForm(BaseDBForm):
	__metaclass__ = DBFormMetaclass
	instance = None