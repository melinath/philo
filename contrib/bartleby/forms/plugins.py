from django.forms.models import ModelForm, modelform_factory, BaseInlineFormSet
from django.forms.util import ErrorList
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.helpers import InlineAdminFormSet, InlineAdminForm

"""
class PluginForm(ModelForm):
	subform = None
	
	def __init__(self, instance=None, **kwargs):
		opts = self._meta
		if instance is not None:
			model = instance.item_content_type.model_class()
			
			if instance.item_object_id is None:
				instance = model()
			else:
				instance = model.objects.get_or_create(id=instance.item_object_id)
			
			subform = modelform_factory(model)
			x=self.base_fields
			y=subform.base_fields
			self.base_fields.update(subform.base_fields)
			
			z=dir(self)
			raise Exception
		defaults = {
			'data': None,
			'files': None,
			'auto_id': 'id_%s',
			'prefix': None,
			'initial': None,
			'error_class': ErrorList,
			'label_suffix': ':',
			'empty_permitted': False, 
		}
		defaults.update(kwargs)
		super(PluginForm, self).__init__(instance=instance, **kwargs)
"""


class PluginFormSet(BaseInlineFormSet):
	#def __init__(self, **kwargs):
	#	raise Exception
	
	def add_fields(self, form, index):
		instance = form.instance
		try:
			contenttype = instance.item_content_type
		except ObjectDoesNotExist:
			form.instance_class = None
		else:
			form.instance_class = model = contenttype.model_class()
			subform = modelform_factory(model)
			form.fields.update(subform.base_fields)
		
		super(PluginFormSet, self).add_fields(form, index)


class PluginInlineAdminFormSet(InlineAdminFormSet):
	"""
	A thin wrapper around the normal InlineAdminFormSet to get it to use a different admin form.
	"""
	#def __init__(self, inline, formset, fieldsets, readonly_fields=None, model_admin=None):
	#	raise Exception
	
	def __iter__(self):
		for form, original in zip(self.formset.initial_forms, self.formset.get_queryset()):
			yield PluginInlineAdminForm(self.formset, form, self.fieldsets, self.opts.prepopulated_fields, original, self.readonly_fields, model_admin=self.model_admin)
		
		for form in self.formset.extra_forms:
			yield PluginInlineAdminForm(self.formset, form, self.fieldsets, self.opts.prepopulated_fields, None, self.readonly_fields, model_admin=self.model_admin)
		
		yield PluginInlineAdminForm(self.formset, self.formset.empty_form, self.fieldsets, self.opts.prepopulated_fields, None, self.readonly_fields, model_admin=self.model_admin)


class PluginInlineAdminForm(InlineAdminForm):
	"""
	Wraps the InlineAdminForm to feed it the correct fieldset depending on the object.
	"""
	def __init__(self, formset, form, fieldsets, prepopulated_fields, original, readonly_fields=None, model_admin=None):
		try:
			fieldsets = fieldsets[form.instance_class]
		except (KeyError, AttributeError, ObjectDoesNotExist):
			fieldsets = fieldsets[None]
		super(PluginInlineAdminForm, self).__init__(formset, form, fieldsets, prepopulated_fields, original, readonly_fields, model_admin)
