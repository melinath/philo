from django.contrib import admin
from philo.contrib.bartleby.models import *
from philo.admin.base import COLLAPSE_CLASSES
from philo.admin import EntityAdmin


class ResultRowInline(admin.TabularInline):
	model = ResultRow


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
	inlines = [FieldInline, ResultRowInline] + EntityAdmin.inlines
	fieldsets = (
		(None, {
			'fields': ('title', 'help_text'),
		}),
		('Processing options', {
			'fields': ('save_to_database', 'email_template', 'email_from', 'email_users', 'email_groups'),
			'classes': COLLAPSE_CLASSES,
		}),
		('Advanced', {
			'fields': ('is_anonymous', 'slug'),
			'classes': COLLAPSE_CLASSES,
		})
	)
	filter_horizontal = ('email_users', 'email_groups')
	prepopulated_fields = {'slug': ('title',)}


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


admin.site.register(Form, FormAdmin)
admin.site.register(Field, FieldAdmin)