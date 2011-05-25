#from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from philo.models import Entity, register_value_model
from philo.utils import ContentTypeSubclassLimiter


#PERSON_MODULE = getattr(settings, 'PHILO_PERSON_MODULE', 'auth.User')


class ResourceSource(models.Model):
	resources = generic.GenericRelation('Resource')
	
	def get_source(self):
		return self.source
	
	class Meta:
		abstract = True


resource_source_contenttype_limiter = ContentTypeSubclassLimiter(ResourceSource)


class FileSource(ResourceSource):
	source = models.FileField(upload_to='edmonia/files/%Y/%m/%d')
	
	class Meta:
		app_label = 'edmonia'


class URLSource(ResourceSource):
	source = models.URLField()
	
	class Meta:
		app_label = 'edmonia'


class Resource(Entity):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	#people = models.ManyToManyField(PERSON_MODULE, through=ResourcePersonMetaInfo, blank=True, null=True)
	creation_date = models.DateField(blank=True, null=True)
	creation_time = models.TimeField(blank=True, null=True)
	timestamp_added = models.DateTimeField(verbose_name="Added to the system")
	timestamp_modified = models.DateTimeField(verbose_name="Last modified")
	
	source_content_type = models.ForeignKey(ContentType, limit_choices_to=resource_source_contenttype_limiter)
	source_object_id = models.PositiveIntegerField()
	source = generic.GenericForeignKey('source_content_type', 'source_object_id')
	
	#notes = models.TextField(blank=True)
	#tags = models.ManyToManyField(blank=True, null=True)
	
	# Include a special relationship to other resources as this is mutual.
	related_resources = models.ManyToManyField('self', blank=True, null=True)
	
	class Meta:
		app_label = 'edmonia'


class ResourceRelated(Entity):
	related_content_type = models.ForeignKey(ContentType)
	related_object_id = models.PositiveIntegerField()
	rel_to = generic.GenericForeignKey('related_content_type', 'related_object_id')
	
	resource = models.ForeignKey(Resource, related_name='related')
	
	class Meta:
		app_label = 'edmonia'


register_value_model(Resource)