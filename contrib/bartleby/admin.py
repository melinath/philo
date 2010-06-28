from django.contrib import admin
from philo.contrib.bartleby.models import *


COLLAPSE_CLOSED_CLASSES = ('collapse', 'closed', 'collapse-closed')


class FormItemInline(admin.TabularInline):
	model = FormItem
	extra = 1


class PageBreakInline(FormItemInline):
	model = PageBreak


class SectionTitleInline(FormItemInline):
	model = SectionTitle


class FieldItemInline(admin.StackedInline):
	model = FieldItem
	extra = 1
	prepopulated_fields = {'key': ('title',)}


class CharFieldInline(FieldItemInline):
	model = CharField


class TextFieldInline(FieldItemInline):
	model = TextField


class RadioChoiceFieldInline(FieldItemInline):
	model = RadioChoiceField


class CheckboxChoiceFieldInline(FieldItemInline):
	model = CheckboxChoiceField


class SelectChoiceFieldInline(FieldItemInline):
	model = SelectChoiceField


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
	inlines = [PageBreakInline, SectionTitleInline, CharFieldInline, TextFieldInline, RadioChoiceFieldInline, CheckboxChoiceFieldInline, SelectChoiceFieldInline]


admin.site.register(FormModel, FormModelAdmin)