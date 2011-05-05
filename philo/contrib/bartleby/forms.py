from django import forms
from django.core.exceptions import ValidationError
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from formwizard.forms import SessionFormWizard


def field_dict_from_instance(instance):
	return SortedDict([(field.key, field.formfield()) for field in instance.fields.order_by('order')])


def honeypot_validator(value):
	if value != "":
		raise ValidationError(_(u'This field must be left blank.'))


class HoneyPotField(forms.Field):
	widget = forms.widgets.HiddenInput
	default_validators = [honeypot_validator]
	
	def __init__(self, required=False, *args, **kwargs):
		super(HoneyPotField, self).__init__(required, *args, **kwargs)


def databaseform_factory(instance, form=forms.Form):
	attrs = field_dict_from_instance(instance)
	attrs.update({
		'instance': instance,
		'_honeypot_field': HoneyPotField()
	})
	return forms.forms.DeclarativeFieldsMetaclass("%sForm" % str(instance.name.replace(' ', '')), (form,), attrs)


class DatabaseFormWizard(SessionFormWizard):
	def __init__(self, form_view, *args, **kwargs):
		self.form_view = form_view
		# Do I need to set kwargs['initial_list'] based on a result row?
		super(DatabaseFormWizard, self).__init__(*args, **kwargs)
	
	def done(self, request, storage, final_form_list, **kwargs):
		return self.form_view.handle_submission(request, final_form_list, **kwargs)
	
	def render(self, request, storage, form, **kwargs):
		return self.form_view.form_display_page.render_to_response(request, extra_context=self.get_template_context(request, storage, form))