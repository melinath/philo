from philo.admin import EntityAdmin
from philo.contrib.edmonia.models import Resource, ResourceRelated
from django.contrib import admin


class ResourceRelatedInline(admin.TabularInline):
	model = ResourceRelated
	verbose_name = "related item"
	verbose_name_plural = "related items"


class ResourceAdmin(EntityAdmin):
	inlines = [ResourceRelatedInline] + EntityAdmin.inlines


admin.site.register(Resource, ResourceAdmin)