from django import forms
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType

from philo.models import Attribute, JSONValue, ForeignKeyValue, ManyToManyValue


__all__ = ('AttributeForm', 'AttributeInlineFormSet')


class AttributeForm(forms.ModelForm):
	def __init__(self, data=None, files=None, *args, **kwargs):
		super(AttributeForm, self).__init__(data, files, *args, **kwargs)
		if self.instance.value_content_type is None:
			self.subform = None
		else:
			model = self.instance.value_content_type.model_class()
			form_class = forms.models.modelform_factory(model)
			self.subform = form_class(data, files, instance=self.instance.value, prefix=self.prefix)
	
	def has_changed(self):
		subform = False if self.subform is None else self.subform.has_changed()
		return super(AttributeForm, self).has_changed() or subform
	
	def full_clean(self):
		super(AttributeForm, self).full_clean()
		if self.subform is not None:
			self.subform.full_clean()
	
	def save(self, *args, **kwargs):
		instance = super(AttributeForm, self).save(*args, **kwargs)
		if self.subform is not None:
			subinstance = self.subform.save()
		return instance
	
	class Meta:
		model = Attribute
		exclude = ('value_object_id',)


class AttributeInlineFormSet(BaseGenericInlineFormSet):
	"Necessary to force the GenericInlineFormset to use the form's save method for new objects."
	def save_new(self, form, commit):
		setattr(form.instance, self.ct_field.get_attname(), ContentType.objects.get_for_model(self.instance).pk)
		setattr(form.instance, self.ct_fk_field.get_attname(), self.instance.pk)
		return form.save()