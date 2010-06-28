"""
A PluginInlineFormset is a Formset of ModelForms belonging to arbitrary pluggable models.
"""


from django.forms.formsets import BaseFormSet, formset_factory
from django.forms.util import ErrorList
from django.forms.models import modelform_factory
from django.forms import IntegerField, HiddenInput, Form, ChoiceField


class MultiFormSetAddFormMetaclass(Form.__metaclass__):
	pass


class MultiFormSetAddForm(Form):
	def __init__(self, *args, **kwargs):
		self.base_fields['form_type'] = ChoiceField(self.CHOICES)
		super(MultiFormSetAddForm, self).__init__(*args, **kwargs)


class BaseMultiFormSet(BaseFormSet):
	"""
	A formset is a "layer of abstraction to working with multiple forms on the same page". A PluginFormSet expands on this idea: it is a layer of abstraction for working with multiple arbitrary forms on the same page. The forms are given as a list instead of as a single form.
	
	Corollary: 'data' passed to basemultiformset should also be a list. => um. not a corollary. And it already is. Did I mean initial, or what?
	
	for each form, I need to save a form type!
	
	Perhaps have a sub-class of ModelForm after all, which has an 'add_view' and 'change_view' based on whether it ... essentially, that adjusts itself. Then make the MultiFormSet adjust to that? No! Just pass an ordered list - where they are.
	"""

	def _construct_form(self, i, **kwargs):
		"""
		Instantiates and returns the i-th form instance in a formset.
		
		This function will first try to instantiate it based on the data, then based on the internal form_class_list. If it can't find one, it'll instantiate an adding form.
		"""
		defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}
		if self.data or self.files:
			defaults['data'] = self.data
			defaults['files'] = self.files
		if self.initial:
			try:
				defaults['initial'] = self.initial[i]
				form_class = self.form_classes[int(self.initial[i]['form_type'])]
			except IndexError:
				pass
		
		# Allow extra forms to be empty.
		if i >= self.initial_form_count():
			defaults['empty_permitted'] = True
		defaults.update(kwargs)
		form = form_class(**defaults)
		self.add_fields(form, i)
		return form
	
	def add_fields(self, form, index):
		form.fields['form_type'] = ChoiceField(self.add_form.CHOICES)
		super(BaseMultiFormSet, self).add_fields(form, index)


def multiformsetadd_factory(multiformset=BaseMultiFormSet, addform=MultiFormSetAddForm, metaclass=MultiFormSetAddFormMetaclass, classes=[]):
	choices = ()
	i = 0
	for form_class in classes:
		choices += ((str(i), classes[i]),)
		i += 1
	
	attrs = {'CHOICES': choices}
	return metaclass(multiformset.__name__+'AddForm', (addform,), attrs)


def multiformset_factory(form_classes, form_class_list=[], formset_name='', formset=BaseMultiFormSet, addform=MultiFormSetAddForm, addform_metaclass=MultiFormSetAddFormMetaclass, extra=1, can_order=False, can_delete=False, max_num=None):
	"""
	Return a MultiFormSet class for the given form classes.
	
	form_classes is a list of classes that can be selected for this formset. Form_class_list is the order of the classes as they are used in the form - otherwise there'd be no way to know which class to instantiate!
	
	Note: this is intentionally generic, and not model-form-specific.
	
	FIXME: a better way to get the `name` would be great.
	"""
	add_form = multiformsetadd_factory(formset, addform, addform_metaclass, form_classes)
	attrs = {'form_classes': form_classes, 'form_class_list': form_class_list, 'extra': extra, 'can_order': can_order, 'can_delete': can_delete, 'max_num': max_num, 'add_form': add_form}
	return type(formset_name + 'MultiFormSet', (formset,), attrs)


def modelmultiformset_factory(model_list, formset_name='Model', formset=BaseMultiFormSet, addform=MultiFormSetAddForm, addform_metaclass=MultiFormSetAddFormMetaclass, extra=1, can_order=False, can_delete=False, max_num=None):
	"""
	Return a MultiFormSet class allowing modelforms for the given models.
	"""
	form_classes = [modelform_factory(model) for model in model_list]
	formset = multiformset_factory(form_classes, formset_name, formset, addform, addform_metaclass, extra, can_order, can_delete, max_num)
	return formset


"""
class PluginForm(ModelForm):
	pass


class BasePluginInlineFormSet(BaseFormSet):
	"""
#	Attempt to make an Inline that generically accepts arbitrary pluggable models. 
#	"""
"""	def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, instance=None, save_as_new=False, queryset=None)
		"""
#		This set of init variables looks a lot like those of a form. probably related. --> It's the init variables on a baseinlineformset.
#		"""
"""		super(BasePluginFormSet, self).__init__(data, files, auto
	
	def get_default_prefix():
		return "prefixtest"
	
	def is_valid():
		return True


class pluginformset_factory


class InlinePluginAdmin(admin.StackedInline):
	"""
#	Options for inline editing of arbitrary plugin models.
#	"""
"""	plugin_mount = None
	plugin_admins = [] # allow passthrough of admin options?
	
	def __init__(self, parent_model, admin_site):
		"parent_model is, for example, FormModel"
		self.parent_model = parent_model
		self.admin_site = admin_site
	
	def get_formset(self, request, obj=None, **kwargs):
"""#		"""Returns a BasePluginFormSet class for use in admin add/change views. Note: this should return a CLASS, not an instance. Use metaclasses to pass options - like probably the plugin list."""
"""		return formset_factory(BasePluginFormSet)
"""