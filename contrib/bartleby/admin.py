from django.contrib import admin
from philo.contrib.bartleby.models import FormModel, FormItem, PageBreak, SectionTitle, FieldItem, CharField, TextField, ChoiceField, ResultRow


COLLAPSE_CLOSED_CLASSES = ('collapse', 'closed', 'collapse-closed')


class SubclassInline(admin.StackedInline):
	def get_formset(self, request, obj):
		pass
	
	def save(self):
		pass
	
	def queryset(self):
		pass
	
	def get_fieldsets(self, request):
		pass
	
	def get_readonly_fields(self, request):
		pass
	
	# Question: ModelAdmin runs inlines through:
	#
	# helpers.InlineAdminFormSet(inline, formset, fieldsets, readonly,
	#		model_admin=self)
	#
	# What's this do, exactly?


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


class ChoiceFieldInline(FieldItemInline):
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