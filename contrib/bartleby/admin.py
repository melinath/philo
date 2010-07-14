from django.contrib import admin
from philo.contrib.bartleby.models import *
from philo.contrib.bartleby.forms.plugins import PluginForm, PluginFormSet, PluginInlineAdminFormSet
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.admin.util import unquote
from django.db import transaction
from django.contrib.admin import helpers
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.forms.formsets import all_valid
from django.http import Http404
from django.contrib.contenttypes import generic


COLLAPSE_CLOSED_CLASSES = ('collapse', 'closed', 'collapse-closed')
csrf_protect_m = method_decorator(csrf_protect)


class AlreadyRegistered(Exception):
	pass


class NotRegistered(Exception):
	pass


class TitledItemAdmin(admin.ModelAdmin):
	pass


class FormFieldAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('title', 'key', 'help_text', 'required')
		}),
	)


class ChoiceOptionInline(generic.GenericInlineModelAdmin):
	model = ChoiceOption
	ct_field = 'field_content_type'
	ct_fk_field = 'field_object_id'
	extra = 1


class ChoiceFieldAdmin(FormFieldAdmin):
	inlines = [ChoiceOptionInline]

	def get_inlines(self, request, obj=None, prefix=None):
		inlines = []
		for inline in self.inline_instances:
			FormSet = inline.get_formset(request, obj)
			prefix = "%s-%s" % (prefix, FormSet.get_default_prefix())
			formset = FormSet(instance=obj, prefix=prefix)
			fieldsets = list(inline.get_fieldsets(request, obj))
			inline = helpers.InlineAdminFormSet(inline, formset, fieldsets)
			inlines.append(inline) 
		return inlines


class PassThrough(object):
	key = None
	
	def __init__(self, dict):
		self.dict = dict
	
	def __call__(self, key=None):
		return self.dict[key]
	
	def __getattr__(self, name):
		return getattr(self(self.key), name)


class PluginDefaultAdmin(admin.options.InlineModelAdmin):
	model = ItemFormRelationship


class PluginInline(admin.options.InlineModelAdmin):
	verbose_name = 'question'
	verbose_name_plural = 'questions'
	template = 'admin/edit_inline/plugin.html'
	formset = PluginFormSet
	form = PluginForm
	plugin_mount = None
	default_admin = PluginDefaultAdmin
	plugins = {}
	
	def __init__(self, parent_model, admin_site):
		for cls in self.plugin_mount.plugins:
			if cls not in self.plugins:
				self.plugins[cls] = admin.ModelAdmin(cls, admin_site)
			elif isinstance(self.plugins[cls], admin.ModelAdmin):
				continue
			else:
				self.plugins[cls] = self.plugins[cls](cls, admin_site)
		
		self.plugins[None] = admin.ModelAdmin(self.model, admin_site)
		self.passthrough = PassThrough(self.plugins)
		
		super(PluginInline, self).__init__(parent_model, admin_site)
	
	@property
	def model(self):
		return self.default_admin.model
	
	def set_fieldsets(self, request, obj=None):
		default = self.get_fieldsets(request, obj)
		
		for admin in self.plugins.values():
			if not admin.fieldsets:
				admin.fieldsets = admin.get_fieldsets(request, obj)
			x=admin.fieldsets
			if admin.fieldsets[0] != default[0]:
				admin.fieldsets = tuple(default) + tuple(admin.fieldsets)
			
	def get_fieldsets(self, request, obj=None):
		"""
		This method shouldn't do anything - this should be handled by the passthrough.
		default = self.plugins[None].get_fieldsets(request, obj)
		fieldsets = {None: default}
		
		for cls, modeladmin in self.plugins.items():
			fs = modeladmin.get_fieldsets(request, obj)
			
			if fs[0] != default[0]:
				fs = tuple(default) + tuple(fs)
			
			fieldsets[cls] = fs
		
		return fieldsets
		"""
		return self.passthrough(None).get_fieldsets(request, obj)
	
	def get_readonly_fields(self, request, obj=None):
		"""
		This method shouldn't do anything - this should be handled by the passthrough.
		readonly = {}
		x=self.plugins
		for cls, modeladmin in self.plugins.items():
			readonly[cls] = modeladmin.get_readonly_fields(request, obj)
		
		return readonly
		"""
		return self.passthrough(None).readonly_fields
	
	@classmethod
	def register(self, plugin, admin_class):
		if plugin in self.plugin_mount.plugins:
			if plugin in self.plugins:
				raise AlreadyRegistered
			
			self.plugins[plugin] = admin_class
		else:
			raise ValueError('%s cannot be registered' % plugin)
	
	@classmethod
	def unregister(self, plugin):
		if plugin not in self.plugins:
			raise NotRegistered
		
		del(self.plugins[plugin])


class FormItemPluginInline(PluginInline):
	plugin_mount = FormItem


class FormModelAdmin(admin.ModelAdmin):
	filter_horizontal=('email_users',)
	fieldsets = (
		(None, {
			'fields': ('title', 'help_text',)
		}),
		('Data handling options', {
			'fields': ('email_users', 'save_to_database',),
			'classes': COLLAPSE_CLOSED_CLASSES
		}),
	)
	plugin_inline = FormItemPluginInline
	
	def __init__(self, model, admin_site):
		super(FormModelAdmin, self).__init__(model, admin_site)
		self.plugin_inline_instance = self.plugin_inline(self.model, self.admin_site)
	
	@csrf_protect_m
	@transaction.commit_on_success
	def change_view(self, request, object_id, extra_context=None):
		"The 'change' admin view for this model."
		model = self.model
		opts = model._meta

		obj = self.get_object(request, unquote(object_id))

		if not self.has_change_permission(request, obj):
			raise PermissionDenied

		if obj is None:
			raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

		if request.method == 'POST' and request.POST.has_key("_saveasnew"):
			return self.add_view(request, form_url='../add/')

		ModelForm = self.get_form(request, obj)
		formsets = []
		if request.method == 'POST':
			form = ModelForm(request.POST, request.FILES, instance=obj)
			if form.is_valid():
				form_validated = True
				new_object = self.save_form(request, form, change=True)
			else:
				form_validated = False
				new_object = obj
			prefixes = {}
			def process_inline(FormSet, inline):
				prefix = FormSet.get_default_prefix()
				prefixes[prefix] = prefixes.get(prefix, 0) + 1
				if prefixes[prefix] != 1:
					prefix = "%s-%s" % (prefix, prefixes[prefix])
				return FormSet(request.POST, request.FILES, instance=new_object, prefix=prefix, queryset=inline.queryset(request))
			
			for FormSet, inline in zip(self.get_formsets(request, new_object), self.inline_instances):
				formsets.append(process_inline(FormSet, inline))
			
			# Custom stuff for the PluginInline
			formset = process_inline(self.plugin_inline_instance.get_formset(request, new_object), self.plugin_inline_instance)
			formsets.append(formset)
			
			# Here I just need to append formset to formsets for validation purposes! I don't need to attach
			# inlines to the correct forms, really.
			
			for _form in formset.forms:
				pt = self.plugin_inline_instance.passthrough
				try:
					pt.key = _form.subform._meta.model
				except AttributeError:
					continue
				
				if pt.inlines:
					obj = _form.instance.item
					for inline in pt.inline_instances:
						FormSet = inline.get_formset(request, obj)
						prefix = '%s-%s' % (_form.prefix, FormSet.get_default_prefix())
						formsets.append(FormSet(request.POST, request.FILES, instance=obj, prefix=prefix, queryset=inline.queryset(request)))
			
			if all_valid(formsets) and form_validated:
				self.save_model(request, new_object, form, change=True)
				form.save_m2m()
				for formset in formsets:
					self.save_formset(request, form, formset, change=True)

				change_message = self.construct_change_message(request, form, formsets)
				self.log_change(request, new_object, change_message)
				return self.response_change(request, new_object)

		else:
			form = ModelForm(instance=obj)
			prefixes = {}
			def process_inline(FormSet, inline, formsets=formsets):
				prefix = FormSet.get_default_prefix()
				prefixes[prefix] = prefixes.get(prefix, 0) + 1
				if prefixes[prefix] != 1:
					prefix = "%s-%s" % (prefix, prefixes[prefix])
				formset = FormSet(instance=obj, prefix=prefix, queryset=inline.queryset(request))
				formsets.append(formset)
			
			for FormSet, inline in zip(self.get_formsets(request, obj), self.inline_instances):
				process_inline(FormSet, inline)
			
			process_inline(self.plugin_inline_instance.get_formset(request, obj), self.plugin_inline_instance)
			

		adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
			self.prepopulated_fields, self.get_readonly_fields(request, obj),
			model_admin=self)
		media = self.media + adminForm.media
		
		inline_admin_formsets = []
		for inline, formset in zip(self.inline_instances, formsets):
			fieldsets = list(inline.get_fieldsets(request, obj))
			readonly = list(inline.get_readonly_fields(request, obj))
			inline_admin_formset = InlineAdminFormSet(inline, formset, fieldsets, readonly, model_admin=self)
			inline_admin_formsets.append(inline_admin_formset)
			media = media + inline_admin_formset.media
		
		# Customized for plugin formsets.
		inline, formset = (self.plugin_inline_instance, formsets[-1])
		inline.set_fieldsets(request, obj)
		inline_admin_formset = PluginInlineAdminFormSet(inline, formset, model_admin=self)	
		
		for _form in formset.forms:
			pt = inline.passthrough
			try:
				pt.key = _form.subform._meta.model
			except AttributeError:
				continue
			
			if pt.inlines:
				if _form.instance.pk:
					instance = _form.instance.item
				else:
					instance = None
				_form.inlines = pt.get_inlines(request, instance, prefix=_form.prefix)
		
		inline_admin_formsets.append(inline_admin_formset)
		media = media + inline_admin_formset.media
		
		context = {
			'title': _('Change %s') % force_unicode(opts.verbose_name),
			'adminform': adminForm,
			'object_id': object_id,
			'original': obj,
			'is_popup': request.REQUEST.has_key('_popup'),
			'media': mark_safe(media),
			'inline_admin_formsets': inline_admin_formsets,
			'errors': helpers.AdminErrorList(form, formsets),
			'root_path': self.admin_site.root_path,
			'app_label': opts.app_label,
		}
		context.update(extra_context or {})
		return self.render_change_form(request, context, change=True, obj=obj)
		

for plugin in FieldItem.plugins:
	if issubclass(plugin, ChoiceField):
		FormItemPluginInline.register(plugin, ChoiceFieldAdmin)
	elif issubclass(plugin, FieldItem):
		FormItemPluginInline.register(plugin, FormFieldAdmin)
	elif issubclass(plugin, TitledFormItem):
		FormItemPluginInline.register(plugin, TitledItemAdmin)
admin.site.register(FormModel, FormModelAdmin)