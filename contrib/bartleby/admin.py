from django.contrib import admin
from philo.contrib.bartleby.models import *
from philo.contrib.bartleby.forms import PluginForm, PluginFormSet, PluginInlineAdminFormSet
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


COLLAPSE_CLOSED_CLASSES = ('collapse', 'closed', 'collapse-closed')
csrf_protect_m = method_decorator(csrf_protect)


class AlreadyRegistered(Exception):
	pass


class NotRegistered(Exception):
	pass


class FormFieldAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {
			'fields': ('title', 'key', 'help_text', 'required')
		}),
	)


class PluginInline(admin.options.InlineModelAdmin):
	model = ItemFormRelationship
	verbose_name = 'question'
	verbose_name_plural = 'questions'
	template = 'admin/edit_inline/plugin.html'
	formset = PluginFormSet
	form = PluginForm
	plugin_mount = FormItem
	plugins = {}
	
	def __init__(self, parent_model, admin_site):
		x=self.plugins
		for cls in self.plugin_mount.plugins:
			if cls not in self.plugins:
				self.plugins[cls] = admin.ModelAdmin(cls, admin_site)
			elif isinstance(self.plugins[cls], admin.ModelAdmin):
				continue
			else:
				self.plugins[cls] = self.plugins[cls](cls, admin_site)
		
		self.plugins[None] = admin.ModelAdmin(self.model, admin_site)
		super(PluginInline, self).__init__(parent_model, admin_site)
	
	def get_fieldsets(self, request, obj=None):
		"This method should return a dictionary of fieldsets, one for each type of plugin."
		default = self.plugins[None].get_fieldsets(request, obj)
		fieldsets = {None: default}
		
		for cls, modeladmin in self.plugins.items():
			fs = modeladmin.get_fieldsets(request, obj)
			
			if fs[0] != default[0]:
				fs = tuple(default) + tuple(fs)
			
			fieldsets[cls] = fs
		
		return fieldsets
	
	def get_readonly_fields(self, request, obj=None):
		"This method should return a dictionary of readonly fields, split by form type."
		readonly = {}
		x=self.plugins
		for cls, modeladmin in self.plugins.items():
			readonly[cls] = modeladmin.get_readonly_fields(request, obj)
		
		return readonly
	
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
	plugin_inline = PluginInline
	
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
			formsets.append(process_inline(self.plugin_inline_instance.get_formset(request, obj), self.plugin_inline_instance))

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
			def process_inline(FormSet, inline):
				prefix = FormSet.get_default_prefix()
				prefixes[prefix] = prefixes.get(prefix, 0) + 1
				if prefixes[prefix] != 1:
					prefix = "%s-%s" % (prefix, prefixes[prefix])
				return FormSet(instance=obj, prefix=prefix, queryset=inline.queryset(request))
			
			for FormSet, inline in zip(self.get_formsets(request, obj), self.inline_instances):
				formsets.append(process_inline(FormSet, inline))
			
			formsets.append(process_inline(self.plugin_inline_instance.get_formset(request, obj), self.plugin_inline_instance))

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
		
		# Customized for plugin formsets. Need to pass the raw fieldsets through as dicts
		inline, formset = (self.plugin_inline_instance, formsets[-1])
		fieldsets = dict(inline.get_fieldsets(request, obj))
		readonly = dict(inline.get_readonly_fields(request, obj))
		inline_admin_formset = PluginInlineAdminFormSet(inline, formset, fieldsets, readonly, model_admin=self)	
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
		

PluginInline.register(TextField, FormFieldAdmin)
PluginInline.register(CharField, FormFieldAdmin)
admin.site.register(FormModel, FormModelAdmin)