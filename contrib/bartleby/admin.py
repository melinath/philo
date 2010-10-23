from django.contrib import admin
from philo.contrib.bartleby.models import *


from philo.admin.base import COLLAPSE_CLASSES


class ResultRowAdmin(admin.TabularInline):
	model = ResultRow


class FieldInline(admin.StackedInline):
	model = Field
	fieldsets = (
		(None, {
			'fields': ('label', 'help_text', ('required', 'multiple'), 'key', 'order'),
		}),
	)
	sortable_field_name = 'order'


class FormAdmin(admin.ModelAdmin):
	inlines = [FieldInline]
	fieldsets = (
		(None, {
			'fields': ('title', 'help_text'),
		}),
		('Processing options', {
			'fields': ('save_to_database', 'email_users', 'email_groups'),
			'classes': COLLAPSE_CLASSES,
		})
	)


class FieldChoiceInline(admin.TabularInline):
	model = FieldChoice


class FieldAdmin(admin.ModelAdmin):
	inlines = [FieldChoiceInline]


admin.site.register(Form, FormAdmin)
admin.site.register(Field, FieldAdmin)