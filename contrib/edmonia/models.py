from django.conf import settings
from django.db import models
from philo.models import Tag, Entity


PERSON_MODULE = getattr(settings, 'PHILO_PERSON_MODULE', 'auth.User')


class AttributionStyle(models.Model):
	# Should this be a OneToOneField? How do we resolve which style to use for a certain object?
	# What if an attribution style changes over time? The old photos should still use the old style; the
	# new photos should use the new style.
	person = models.ForeignKey(PERSON_MODULE, related_name='attribution_styles')
	attribution = models.CharField(max_length=75, help_text="If present, %s will be replaced by the contributor's name.")
	attribution_notes = models.TextField()
	# stop_using = DateTime
	# resource_type = SmallPositiveInteger


CONTRIBUTOR = 1
TAGGED = 2
RESOURCE_PERSON_RELATIONSHIPS = {
	CONTRIBUTOR: 'Contributor',
	TAGGED: 'Tagged'
}
#RESOURCE_PERSON_RELATIONSHIP_CHOICES = RESOURCE_PERSON_RELATIONSHIPS.items()


class ResourcePersonMetaInfo(models.Model):
	person = models.ForeignKey(PERSON_MODULE)
	media = models.ForeignKey('Resource')
	relationship = models.PositiveSmallIntegerField(choices=RESOURCE_PERSON_RELATIONSHIPS.items())


class ResourceTagMetaInfo(models.Model):
	tag = models.ForeignKey(Tag)
	media = models.ForeignKey('Resource')
	is_curated = models.BooleanField()


PHOTOGRAPH = 1
VIDEO = 2
GRAPHIC = 3
RESOURCE_TYPES = {
	PHOTOGRAPH: 'Photograph',
	VIDEO: 'Video',
	GRAPHIC: 'Graphic'
}


# Probably implement usage limitations with a series of plugins and a JSON field. The plugins control how
# the field data is interpreted. Ack, though - some limitations may vary depending on what type of resource
# we're dealing with. Each should blacklist or whitelist resource types so that forms can decide which ones
# to use without knowing anything about them.
USAGE_LIMITATIONS = {
	#print only: true/false
	#until date: datetime
	#size/resolution: paired integers (floats?)
	#other: text field
}


class Resource(Entity):
	people = models.ManyToManyField(PERSON_MODULE, through=ResourcePersonMetaInfo)
	caption = models.TextField(blank=True)
	
	# Location should probably be tied into some sort of generic "Location" model that could also be used
	# for event venues. Where would this model sit?
	location = models.TextField(blank=True)
	
	creation_date = models.DateField(blank=True, null=True)
	creation_time = models.TimeField(blank=True, null=True)
	timestamp = models.DateTimeField(help_text="Date the photo was added to the system")
	
	usage_limitations = models.CommaSeparatedIntegerField(max_length=255, blank=True, choices=USAGE_LIMITATIONS.items())
	type = models.PositiveSmallIntegerField(choices=RESOURCE_TYPES.items())
	# event?
	
	# `source` may refer to various things: for a photograph entered into the system, the source could be
	# digital/negative/photo; for a video, it could be digital/film/etc. These distinctions are relevant to
	# the forms used to manage this model, not to the model itself.
	source = models.CharField(max_length=50)
	
	notes = models.TextField()
	tags = models.ManyToManyField(blank=True, null=True, through=ResourceTagMetaInfo)
	related_resources = models.ManyToManyField('self')


# class ResourceRelationToSomething
#     It was mentioned that photos should have a relationship with anything that allowed for a caption and
#     additional cropping information. Can this idea be genericized? Or would it perhaps be best to provide
#     an abstract model that's easy to subclass and have a relationship through?