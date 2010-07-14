from django.forms.models import ModelForm, modelform_factory, BaseInlineFormSet
from django.forms.util import ErrorList, ErrorDict
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.helpers import InlineAdminFormSet, InlineAdminForm
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext
from django.contrib.contenttypes.models import ContentType


class PluginSubForm(ModelForm):
	def has_changed(self):
		instance = self.parent.instance
		if instance._item != instance.item:
			return False
		
		return super(PluginSubForm, self).has_changed()
	
	def _post_clean(self):
		# I need to save the sub-item's id.
		# Cases:
		# 1. There is no sub-item. id=None.
		# 2. sub-item contenttype the same. id = subitem.id
		# 3. sub-item contenttype changed. id=None
		instance = self.parent.instance
		old = instance._item
		old_ct = instance._item_content_type
		new_ct = instance.item_content_type
		
		if old is None or old_ct != new_ct:
			id = None
		else:
			id = old.id
		
		self.cleaned_data['id'] = id
		
		super(PluginSubForm, self)._post_clean()


class PluginForm(ModelForm):
	subform = None
	subformclass = None
	
	def __init__(self, *args, **kwargs):
		super(PluginForm, self).__init__(*args, **kwargs)
		
		if self.instance:
			try:
				contenttype = self.instance.item_content_type
			except ObjectDoesNotExist:
				pass
			else:
				model = contenttype.model_class()
				self.subformclass = modelform_factory(model, form=PluginSubForm)
				
				#Now try to get the related instance to instantiate to subform!
				kwargs.update({
					'instance': self.instance.item
				})
				self.subform = self.subformclass(*args, **kwargs)
				self.subform.parent = self
				initial = self.subform.initial
				if 'id' in initial:
					del(initial['id'])
				self.initial.update(initial)
	
	def is_valid(self):
		subform_valid = True
		
		if self.subform is not None:
			subform_valid = self.subform.is_valid()
		
		return super(PluginForm, self).is_valid() and subform_valid
	
	def save(self, commit=True):
		if self.subform is not None:
			self.instance.item = self.subform.save()
		return super(PluginForm, self).save(commit)


class PluginFormSet(BaseInlineFormSet):
	#def __init__(self, **kwargs):
	#	raise Exception
	
	def add_fields(self, form, index):
		if form.subform is not None:
			form.fields.update(form.subform.fields)
		
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
			fieldsets = fieldsets[form.subformclass._meta.model]
		except (KeyError, AttributeError,):
			fieldsets = fieldsets[None]
		super(PluginInlineAdminForm, self).__init__(formset, form, fieldsets, prepopulated_fields, original, readonly_fields, model_admin)
