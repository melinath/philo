from django import forms
from django.contrib.admin import widgets
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType

from philo.models import Attribute, JSONValue, ForeignKeyValue, ManyToManyValue


__all__ = ('AttributeForm', 'AttributeInlineFormSet')


class ManyToManyValueForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(ManyToManyValueForm, self).__init__(*args, **kwargs)
		if self.instance.content_type is not None:
			model = self.instance.content_type.model_class()
			self.fields['value'] = forms.models.ModelMultipleChoiceField(model.objects.all(), widget=widgets.FilteredSelectMultiple(model._meta.verbose_name_plural, False), initial=self.instance.value, required=False)
		else:
			self.fields['value'] = forms.MultipleChoiceField(widget=widgets.FilteredSelectMultiple('', False), required=False)
	
	def save(self, *args, **kwargs):
		instance = super(ManyToManyValueForm, self).save(*args, **kwargs)
		model = instance.content_type.model_class()
		qs = model._default_manager.filter(pk__in=self.cleaned_data.get('value', []))
		instance.set_value(qs)
		return instance
	
	class Meta:
		model = ManyToManyValue
		exclude = ('values',)


class AttributeForm(forms.ModelForm):
	def __init__(self, data=None, files=None, *args, **kwargs):
		super(AttributeForm, self).__init__(data, files, *args, **kwargs)
		if self.instance.value_content_type is None:
			self.subform = None
		else:
			model = self.instance.value_content_type.model_class()
			if model is ManyToManyValue:
				form_class = ManyToManyValueForm
			else:
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
	
	def _get_media(self):
		media = super(AttributeForm, self)._get_media()
		if self.subform:
			media += self.subform._get_media()
		return media
	media = property(_get_media)
	
	class Meta:
		model = Attribute
		exclude = ('value_object_id',)


class AttributeInlineFormSet(BaseGenericInlineFormSet):
	"Necessary to force the GenericInlineFormset to use the form's save method for new objects."
	def save_new(self, form, commit):
		setattr(form.instance, self.ct_field.get_attname(), ContentType.objects.get_for_model(self.instance).pk)
		setattr(form.instance, self.ct_fk_field.get_attname(), self.instance.pk)
		return form.save()
	
	def _get_empty_form(self, **kwargs):
		form = super(AttributeInlineFormSet, self)._get_empty_form(**kwargs)
		kwargs = {
			'auto_id': form.auto_id,
			'prefix': form.prefix,
			'empty_permitted': True,
		}
		form.subforms = [
			forms.models.modelform_factory(JSONValue)(**kwargs),
			forms.models.modelform_factory(ForeignKeyValue)(**kwargs),
			ManyToManyValueForm(**kwargs),
		]
		return form
	empty_form = property(_get_empty_form)