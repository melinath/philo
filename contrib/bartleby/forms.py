"""
The Bartleby forms center around a central object: the DatabaseForm, so called
because it is a form created based on database input.
"""


from django.forms.forms import Form, DeclarativeFieldsMetaclass
from django.utils.datastructures import SortedDict


class DatabaseForm(Form):
	"Contains functionality specific to database-driven forms."
	pass


def field_dict_from_instance(instance):
	return SortedDict([(field.key, field.formfield()) for field in instance.fields.order_by('order')])


def databaseform_factory(instance, form=DatabaseForm):
	return DeclarativeFieldsMetaclass("%sForm" % str(instance.title.replace(' ', '')), (form,), field_dict_from_instance(instance))