from django.contrib import admin
from philo.contrib.bartleby.models import FormModel, FormItem, PageBreak, SectionTitle, CharField, TextField, ChoiceField, ResultRow


COLLAPSE_CLOSED_CLASSES = ('collapse', 'closed', 'collapse-closed')


class FormItemInline(admin.TabularInline):
	model = FormItem
	extra = 1


class PageBreakInline(FormItemInline):
	model = PageBreak


class SectionTitleInline(FormItemInline):
	model = SectionTitle


class CharFieldInline(FormItemInline):
	model = CharField


class TextFieldInline(FormItemInline):
	model = TextField


class ChoiceFieldInline(FormItemInline):
	model = ChoiceField


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
	inlines = [PageBreakInline, SectionTitleInline, CharFieldInline, TextFieldInline, ChoiceFieldInline]


admin.site.register(FormModel, FormModelAdmin)