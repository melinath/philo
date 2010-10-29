from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from philo.contrib.bartleby.models import Form
from philo.models import Attribute, Entity


def get_entity_forms(entity, passthrough=True):
	if not isinstance(entity, Entity):
		raise TypeError
	
	# Iterating over an entity's attributes and passthroughs should take more
	# SQL work than a single complex query, but the results are more complete.
	# Can this be verified?
	if passthrough and entity.attributes.passthrough is not None:
		form_ct = ContentType.objects.get_for_model(Form)
		exclude_keys = set() # Exclude keys already found
		
		def get_attribute_forms(qs_mapper):
			forms = set()
			for attribute in qs_mapper.queryset.exclude(key__in=exclude_keys):
				if hasattr(attribute.value, 'content_type') and attribute.value.content_type == form_ct:
					try:
						forms |= set(attribute.value.value)
					except TypeError:
						# Then it wasn't iterable - i.e. it was a ForeignKeyValue
						forms.add(attribute.value.value)
					exclude_keys.add(attribute.key)
			
			if qs_mapper.passthrough:
				forms |= get_attribute_forms(qs_mapper.passthrough)
			
			return forms
		
		return get_attribute_forms(entity.attributes)
	
	entity_ct = ContentType.objects.get_for_model(entity)
	
	fk_q = Q(foreignkeyvalue_set__attribute_set__entity_content_type=entity_ct) & Q(foreignkeyvalue_set__attribute_set__entity_object_id=entity.pk)
	m2m_q = Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__entity_content_type=entity_ct) & Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__entity_object_id=entity.pk)
	
	forms = Form.objects.filter(fk_q | (~fk_q & m2m_q))
	
	return forms