from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import simplejson as json
from django.utils.encoding import force_unicode
from mptt.models import MPTTModel, MPTTModelBase, MPTTOptions

from philo.exceptions import AncestorDoesNotExist
from philo.models.fields import JSONField
from philo.signals import entity_class_prepared
from philo.utils import ContentTypeRegistryLimiter, ContentTypeSubclassLimiter
from philo.utils.entities import AttributeMapper, TreeAttributeMapper
from philo.validators import json_validator


__all__ = ('value_content_type_limiter', 'register_value_model', 'unregister_value_model', 'JSONValue', 'ForeignKeyValue', 'ManyToManyValue', 'Attribute', 'Entity', 'TreeEntity', 'SlugTreeEntity')


#: An instance of :class:`.ContentTypeRegistryLimiter` which is used to track the content types which can be related to by :class:`ForeignKeyValue`\ s and :class:`ManyToManyValue`\ s.
value_content_type_limiter = ContentTypeRegistryLimiter()


def register_value_model(model):
	"""Registers a model as a valid content type for a :class:`ForeignKeyValue` or :class:`ManyToManyValue` through the :data:`value_content_type_limiter`."""
	value_content_type_limiter.register_class(model)


def unregister_value_model(model):
	"""Registers a model as a valid content type for a :class:`ForeignKeyValue` or :class:`ManyToManyValue` through the :data:`value_content_type_limiter`."""
	value_content_type_limiter.unregister_class(model)


class AttributeValue(models.Model):
	"""
	This is an abstract base class for models that can be used as values for :class:`Attribute`\ s.
	
	AttributeValue subclasses are expected to supply access to a clean version of their value through an attribute called "value".
	
	"""
	
	#: :class:`GenericRelation` to :class:`Attribute`
	attribute_set = generic.GenericRelation('Attribute', content_type_field='value_content_type', object_id_field='value_object_id')
	
	def set_value(self, value):
		"""Given a ``value``, sets the appropriate fields so that it can be correctly stored in the database."""
		raise NotImplementedError
	
	def __unicode__(self):
		return unicode(self.value)
	
	class Meta:
		abstract = True


#: An instance of :class:`.ContentTypeSubclassLimiter` which is used to track the content types which are considered valid value models for an :class:`Attribute`.
attribute_value_limiter = ContentTypeSubclassLimiter(AttributeValue)


class JSONValue(AttributeValue):
	"""Stores a python object as a json string."""
	value = JSONField(verbose_name='Value (JSON)', help_text='This value must be valid JSON.', default='null', db_index=True)
	
	def __unicode__(self):
		return force_unicode(self.value)
	
	def set_value(self, value):
		self.value = value
	
	class Meta:
		app_label = 'philo'


class ForeignKeyValue(AttributeValue):
	"""Stores a generic relationship to an instance of any value content type (as defined by the :data:`value_content_type_limiter`)."""
	content_type = models.ForeignKey(ContentType, limit_choices_to=value_content_type_limiter, verbose_name='Value type', null=True, blank=True)
	object_id = models.PositiveIntegerField(verbose_name='Value ID', null=True, blank=True, db_index=True)
	value = generic.GenericForeignKey()
	
	def set_value(self, value):
		self.value = value
	
	class Meta:
		app_label = 'philo'


class ManyToManyValue(AttributeValue):
	"""Stores a generic relationship to many instances of any value content type (as defined by the :data:`value_content_type_limiter`)."""
	content_type = models.ForeignKey(ContentType, limit_choices_to=value_content_type_limiter, verbose_name='Value type', null=True, blank=True)
	values = models.ManyToManyField(ForeignKeyValue, blank=True, null=True)
	
	def get_object_ids(self):
		return self.values.values_list('object_id', flat=True)
	object_ids = property(get_object_ids)
	
	def set_value(self, value):
		# Value must be a queryset. Watch out for ModelMultipleChoiceField;
		# it returns its value as a list if empty.
		
		self.content_type = ContentType.objects.get_for_model(value.model)
		
		# Before we can fiddle with the many-to-many to foreignkeyvalues, we need
		# a pk.
		if self.pk is None:
			self.save()
		
		object_ids = value.values_list('id', flat=True)
		
		# These lines shouldn't be necessary; however, if object_ids is an EmptyQuerySet,
		# the code (specifically the object_id__in query) won't work without them. Unclear why...
		# TODO: is this still the case?
		if not object_ids:
			self.values.all().delete()
		else:
			self.values.exclude(object_id__in=object_ids, content_type=self.content_type).delete()
			
			current_ids = self.object_ids
			
			for object_id in object_ids:
				if object_id in current_ids:
					continue
				self.values.create(content_type=self.content_type, object_id=object_id)
	
	def get_value(self):
		if self.content_type is None:
			return None
		
		# HACK to be safely explicit until http://code.djangoproject.com/ticket/15145 is resolved
		object_ids = self.object_ids
		manager = self.content_type.model_class()._default_manager
		if not object_ids:
			return manager.none()
		return manager.filter(id__in=self.object_ids)
	
	value = property(get_value, set_value)
	
	class Meta:
		app_label = 'philo'


class Attribute(models.Model):
	"""
	:class:`Attribute`\ s exist primarily to let arbitrary data be attached to arbitrary model instances without altering the database schema and without guaranteeing that the data will be available on every instance of that model.
	
	Generally, :class:`Attribute`\ s will not be accessed as models; instead, they will be accessed through the :attr:`Entity.attributes` property, which allows direct dictionary getting and setting of the value of an :class:`Attribute` with its key.
	
	"""
	entity_content_type = models.ForeignKey(ContentType, related_name='attribute_entity_set', verbose_name='Entity type')
	entity_object_id = models.PositiveIntegerField(verbose_name='Entity ID', db_index=True)
	
	#: :class:`GenericForeignKey` to anything (generally an instance of an Entity subclass).
	entity = generic.GenericForeignKey('entity_content_type', 'entity_object_id')
	
	value_content_type = models.ForeignKey(ContentType, related_name='attribute_value_set', limit_choices_to=attribute_value_limiter, verbose_name='Value type', null=True, blank=True)
	value_object_id = models.PositiveIntegerField(verbose_name='Value ID', null=True, blank=True, db_index=True)
	
	#: :class:`GenericForeignKey` to an instance of a subclass of :class:`AttributeValue` as determined by the :data:`attribute_value_limiter`.
	value = generic.GenericForeignKey('value_content_type', 'value_object_id')
	
	#: :class:`CharField` containing a key (up to 255 characters) consisting of alphanumeric characters and underscores.
	key = models.CharField(max_length=255, validators=[RegexValidator("\w+")], help_text="Must contain one or more alphanumeric characters or underscores.", db_index=True)
	
	def __unicode__(self):
		ct = ContentType.objects.get_for_id(self.value_content_type_id)
		value_type = ct.model_class()
		uni = u'"%s": %s' % (self.key, value_type._meta.verbose_name)
		
		if self.value_object_id is not None:
			uni = u'%s: %s' % (uni, self.value)
		
		return uni
	
	def set_value(self, value, value_class=JSONValue):
		"""Given a value and a value class, sets up self.value appropriately."""
		if isinstance(self.value, value_class):
			val = self.value
		else:
			if isinstance(self.value, models.Model):
				self.value.delete()
			val = value_class()
		
		val.set_value(value)
		val.save()
		
		self.value = val
		self.save()
	
	class Meta:
		app_label = 'philo'
		unique_together = (('key', 'entity_content_type', 'entity_object_id'), ('value_content_type', 'value_object_id'))


class EntityOptions(object):
	def __init__(self, options):
		if options is not None:
			for key, value in options.__dict__.items():
				setattr(self, key, value)
		if not hasattr(self, 'proxy_fields'):
			self.proxy_fields = []
	
	def add_proxy_field(self, proxy_field):
		self.proxy_fields.append(proxy_field)


class EntityBase(models.base.ModelBase):
	def __new__(cls, name, bases, attrs):
		entity_meta = attrs.pop('EntityMeta', None)
		new = super(EntityBase, cls).__new__(cls, name, bases, attrs)
		new.add_to_class('_entity_meta', EntityOptions(entity_meta))
		entity_class_prepared.send(sender=new)
		return new


class Entity(models.Model):
	"""An abstract class that simplifies access to related attributes. Most models provided by Philo subclass Entity."""
	__metaclass__ = EntityBase
	
	attribute_set = generic.GenericRelation(Attribute, content_type_field='entity_content_type', object_id_field='entity_object_id')
	
	def get_attribute_mapper(self, mapper=AttributeMapper):
		"""
		Returns an :class:`.AttributeMapper` which can be used to retrieve related :class:`Attribute`\ s' values directly.

		Example::

			>>> attr = entity.attribute_set.get(key='spam')
			>>> attr.value.value
			u'eggs'
			>>> entity.attributes['spam']
			u'eggs'
		
		"""
		return mapper(self)
	
	@property
	def attributes(self):
		if not hasattr(self, '_attributes'):
			self._attributes = self.get_attribute_mapper()
		return self._attributes
	
	class Meta:
		abstract = True


class TreeEntityBase(MPTTModelBase, EntityBase):
	def __new__(meta, name, bases, attrs):
		attrs['_mptt_meta'] = MPTTOptions(attrs.pop('MPTTMeta', None))
		cls = EntityBase.__new__(meta, name, bases, attrs)
		
		return meta.register(cls)


class TreeEntityManager(models.Manager):
	use_for_related_fields = True
	
	def get_with_path(self, path, root=None, absolute_result=True, pathsep='/', field='pk'):
		"""
		If ``absolute_result`` is ``True``, returns the object at ``path`` (starting at ``root``) or raises an :class:`~django.core.exceptions.ObjectDoesNotExist` exception. Otherwise, returns a tuple containing the deepest object found along ``path`` (or ``root`` if no deeper object is found) and the remainder of the path after that object as a string (or None if there is no remaining path).
		
		.. note:: If you are looking for something with an exact path, it is faster to use absolute_result=True, unless the path depth is over ~40, in which case the high cost of the absolute query may make a binary search (i.e. non-absolute) faster.
		
		.. note:: SQLite allows max of 64 tables in one join. That means the binary search will only work on paths with a max depth of 127 and the absolute fetch will only work to a max depth of (surprise!) 63. Larger depths could be handled, but since the common use case will not have a tree structure that deep, they are not.
		
		:param path: The path of the object
		:param root: The object which will be considered the root of the search
		:param absolute_result: Whether to return an absolute result or do a binary search
		:param pathsep: The path separator used in ``path``
		:param field: The field on the model which should be queried for ``path`` segment matching.
		:returns: An instance if ``absolute_result`` is ``True`` or an (instance, remaining_path) tuple otherwise.
		:raises django.core.exceptions.ObjectDoesNotExist: if no object can be found matching the input parameters.
		
		"""
		
		segments = path.split(pathsep)
		
		# Clean out blank segments. Handles multiple consecutive pathseps.
		while True:
			try:
				segments.remove('')
			except ValueError:
				break
		
		# Special-case a lack of segments. No queries necessary.
		if not segments:
			if root is not None:
				if absolute_result:
					return root
				return root, None
			else:
				raise self.model.DoesNotExist('%s matching query does not exist.' % self.model._meta.object_name)
		
		def make_query_kwargs(segments, root):
			kwargs = {}
			prefix = ""
			revsegs = list(segments)
			revsegs.reverse()
			
			for segment in revsegs:
				kwargs["%s%s__exact" % (prefix, field)] = segment
				prefix += "parent__"
			
			if prefix:
				kwargs[prefix[:-2]] = root
			
			return kwargs
		
		def find_obj(segments, depth, deepest_found=None):
			if deepest_found is None:
				deepest_level = 0
			elif root is None:
				deepest_level = deepest_found.get_level() + 1
			else:
				deepest_level = deepest_found.get_level() - root.get_level()
			try:
				obj = self.get(**make_query_kwargs(segments[deepest_level:depth], deepest_found or root))
			except self.model.DoesNotExist:
				if not deepest_level and depth > 1:
					# make sure there's a root node...
					depth = 1
				else:
					# Try finding one with half the path since the deepest find.
					depth = (deepest_level + depth)/2
				
				if deepest_level == depth:
					# This should happen if nothing is found with any part of the given path.
					if root is not None and deepest_found is None:
						return root, pathsep.join(segments)
					raise
				
				return find_obj(segments, depth, deepest_found)
			else:
				# Yay! Found one!
				if root is None:
					deepest_level = obj.get_level() + 1
				else:
					deepest_level = obj.get_level() - root.get_level()
				
				# Could there be a deeper one?
				if obj.is_leaf_node():
					return obj, pathsep.join(segments[deepest_level:]) or None
				
				depth += (len(segments) - depth)/2 or len(segments) - depth
				
				if depth > deepest_level + obj.get_descendant_count():
					depth = deepest_level + obj.get_descendant_count()
				
				if deepest_level == depth:
					return obj, pathsep.join(segments[deepest_level:]) or None
				
				try:
					return find_obj(segments, depth, obj)
				except self.model.DoesNotExist:
					# Then this was the deepest.
					return obj, pathsep.join(segments[deepest_level:])
		
		if absolute_result:
			return self.get(**make_query_kwargs(segments, root))
		
		# Try a modified binary search algorithm. Feed the root in so that query complexity
		# can be reduced. It might be possible to weight the search towards the beginning
		# of the path, since short paths are more likely, but how far forward? It would
		# need to shift depending on len(segments) - perhaps logarithmically?
		return find_obj(segments, len(segments)/2 or len(segments))


class TreeEntity(Entity, MPTTModel):
	"""An abstract subclass of Entity which represents a tree relationship."""
	
	__metaclass__ = TreeEntityBase
	objects = TreeEntityManager()
	parent = models.ForeignKey('self', related_name='children', null=True, blank=True)
	
	def get_path(self, root=None, pathsep='/', field='pk', memoize=True):
		"""
		:param root: Only return the path since this object.
		:param pathsep: The path separator to use when constructing an instance's path
		:param field: The field to pull path information from for each ancestor.
		:param memoize: Whether to use memoized results. Since, in most cases, the ancestors of a TreeEntity will not change over the course of an instance's lifetime, this defaults to ``True``.
		:returns: A string representation of an object's path.
		
		"""
		
		if root == self:
			return ''
		
		parent_id = getattr(self, "%s_id" % self._mptt_meta.parent_attr)
		if getattr(root, 'pk', None) == parent_id:
			return getattr(self, field, '?')
		
		if root is not None and not self.is_descendant_of(root):
			raise AncestorDoesNotExist(root)
		
		if memoize:
			memo_args = (parent_id, getattr(root, 'pk', None), pathsep, getattr(self, field, '?'))
			try:
				return self._path_memo[memo_args]
			except AttributeError:
				self._path_memo = {}
			except KeyError:
				pass
		
		qs = self.get_ancestors(include_self=True)
		
		if root is not None:
			qs = qs.filter(**{'%s__gt' % self._mptt_meta.level_attr: root.get_level()})
		
		path = pathsep.join([getattr(parent, field, '?') for parent in qs])
		
		if memoize:
			self._path_memo[memo_args] = path
		
		return path
	path = property(get_path)
	
	def get_attribute_mapper(self, mapper=None):
		"""
		Returns a :class:`.TreeAttributeMapper` or :class:`.AttributeMapper` which can be used to retrieve related :class:`Attribute`\ s' values directly. If an :class:`Attribute` with a given key is not related to the :class:`Entity`, then the mapper will check the parent's attributes.

		Example::

			>>> attr = entity.attribute_set.get(key='spam')
			DoesNotExist: Attribute matching query does not exist.
			>>> attr = entity.parent.attribute_set.get(key='spam')
			>>> attr.value.value
			u'eggs'
			>>> entity.attributes['spam']
			u'eggs'
		
		"""
		if mapper is None:
			if getattr(self, "%s_id" % self._mptt_meta.parent_attr):
				mapper = TreeAttributeMapper
			else:
				mapper = AttributeMapper
		return super(TreeEntity, self).get_attribute_mapper(mapper)
	
	def __unicode__(self):
		return self.path
	
	class Meta:
		abstract = True


class SlugTreeEntityManager(TreeEntityManager):
	def get_with_path(self, path, root=None, absolute_result=True, pathsep='/', field='slug'):
		return super(SlugTreeEntityManager, self).get_with_path(path, root, absolute_result, pathsep, field)


class SlugTreeEntity(TreeEntity):
	objects = SlugTreeEntityManager()
	slug = models.SlugField(max_length=255)
	
	def get_path(self, root=None, pathsep='/', field='slug', memoize=True):
		return super(SlugTreeEntity, self).get_path(root, pathsep, field, memoize)
	path = property(get_path)
	
	def clean(self):
		if getattr(self, "%s_id" % self._mptt_meta.parent_attr) is None:
			try:
				self._default_manager.exclude(pk=self.pk).get(slug=self.slug, parent__isnull=True)
			except self.DoesNotExist:
				pass
			else:
				raise ValidationError(self.unique_error_message(self.__class__, ('parent', 'slug')))
	
	class Meta:
		unique_together = ('parent', 'slug')
		abstract = True