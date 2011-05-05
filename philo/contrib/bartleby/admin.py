from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext_lazy as _

from philo.contrib.bartleby.helpers import FormView as FormViewHelper
from philo.contrib.bartleby.models import Field, Form, FieldValue, ResultRow, FieldChoice, FormView, FormStep
from philo.admin.base import COLLAPSE_CLASSES
from philo.admin import EntityAdmin, PageAdmin
from philo.forms import EntityForm


class FieldInline(admin.StackedInline):
	model = Field
	fieldsets = (
		(None, {
			'fields': ('label', 'help_text', ('required', 'multiple'), 'key', 'order'),
		}),
	)
	sortable_field_name = 'order'
	prepopulated_fields = {'key': ('label',)}


class FormAdmin(EntityAdmin):
	inlines = [FieldInline] + EntityAdmin.inlines
	prepopulated_fields = {'key': ('name',)}


class FieldChoiceInline(admin.TabularInline):
	model = FieldChoice
	verbose_name = 'choice'
	verbose_name_plural = 'choices'
	sortable_field_name = 'order'
	fields = ('verbose_name', 'key', 'order')
	prepopulated_fields = {'key': ('verbose_name',)}


class FieldAdmin(admin.ModelAdmin):
	inlines = [FieldChoiceInline]
	fieldsets = (
		(None, {
			'fields': ('label', 'help_text', ('required', 'multiple'), 'form'),
		}),
		('Advanced', {
			'fields': ('key', 'order'),
			'classes': COLLAPSE_CLASSES
		})
	)
	prepopulated_fields = {'key': ('label',)}


class FieldValueInline(admin.TabularInline):
	model = FieldValue
	raw_id_fields = ('field',)


class ResultRowAdmin(admin.ModelAdmin):
	inlines = [FieldValueInline]
	list_display = ('submitter', 'form_view', 'submitted')
	date_hierarchy = 'submitted'
	readonly_fields = ('submitter',)
	fieldsets = (
		(None, {
			'fields': ('submitter', 'submitted', 'form_view')
		}),
		('Advanced', {
			'fields': ('user', 'ip_address', 'cookie',)
		})
	)
	raw_id_fields = ('form_view', 'user')
	search_fields = ('user__first_name', 'user__last_name', 'user__username', 'ip_address', 'cookie')
	list_filter = ('form_view',)


class FormStepInline(admin.TabularInline):
	model = FormStep
	sortable_field_name = 'order'
	raw_id_fields = ('form',)


class FormViewAdmin(EntityAdmin):
	inlines = [FormStepInline]
	raw_id_fields = ('form_display_page', 'form_complete_page', 'results_email_page')
	fieldsets = (
		(None, {
			'fields': ('name', 'form_display_page', 'form_complete_page'),
		}),
		('Processing options', {
			'fields': ('save_to_database', 'results_email_page', 'results_email_sender', 'email_users', 'email_groups'),
			'classes': COLLAPSE_CLASSES,
		}),
		('Advanced', {
			'fields': ('record', 'login_required', 'allow_changes', 'max_submissions'),
			'classes': COLLAPSE_CLASSES,
		})
	)
	filter_horizontal = ('email_users', 'email_groups')
	radio_fields = {'record': admin.VERTICAL}
	if 'grappelli' in settings.INSTALLED_APPS:
		view_results_template = "admin/bartleby/form/grappelli_view_results.html"
	else:
		view_results_template = "admin/bartleby/form/view_results.html"
	actions = ['results_redirect']
	
	def get_urls(self):
		from django.conf.urls.defaults import patterns, url
		
		def wrap(view):
			def wrapper(*args, **kwargs):
				return self.admin_site.admin_view(view)(*args, **kwargs)
			return update_wrapper(wrapper, view)
		
		urlpatterns = patterns('',
			url(r'^results/$', wrap(self.view_results), name='%s_%s_view_results' % (self.model._meta.app_label, self.model._meta.module_name))
		) + super(FormViewAdmin, self).get_urls()
		return urlpatterns
	
	def view_results(self, request):
		formviews = [FormViewHelper(formview, index, request) for index, formview in enumerate(self.model._default_manager.filter(pk__in=request.GET['pks'].split(',')))]
		c = {
			'formviews': formviews,
			'app_label': self.model._meta.app_label,
			'title': _('View form results')
		}
		return render_to_response(self.view_results_template, c, context_instance=RequestContext(request))
	
	def results_redirect(self, request, queryset):
		selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		return HttpResponseRedirect("%s?pks=%s" % (reverse('admin:%s_%s_view_results' % (self.model._meta.app_label, self.model._meta.module_name)), ','.join(selected)))
	results_redirect.short_description = _("View form results")


admin.site.register(Form, FormAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(ResultRow, ResultRowAdmin)
admin.site.register(FormView, FormViewAdmin)