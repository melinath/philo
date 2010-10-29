from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from philo.contrib.bartleby.models import Form
from philo.models import Attribute, Entity


def get_entity_forms(entity, passthrough=True):
	if not isinstance(entity, Entity):
		raise TypeError
	
	if passthrough and entity.attributes.passthrough is not None:
		exclude_keys = [] # Exclude keys already found
		
		def get_attribute_forms(qs_mapper):
			qs = Form.objects.none()
			
			for attribute in qs_mapper.queryset.exclude(key__in=exclude_keys):
				fk_q = Q(foreignkeyvalue_set__attribute_set=attribute)
				m2m_q = Q(foreignkeyvalue_set__manytomanyvalue__attribute_set=attribute)
				
				qs |= Form.objects.filter(fk_q | m2m_q)
				exclude_keys.append(attribute.key)
			
			if qs_mapper.passthrough:
				qs |= get_attribute_forms(qs_mapper.passthrough)
			
			return qs
		
		return get_attribute_forms(entity.attributes).distinct()
	
	entity_ct = ContentType.objects.get_for_model(entity)
	
	fk_q = Q(foreignkeyvalue_set__attribute_set__entity_content_type=entity_ct) & Q(foreignkeyvalue_set__attribute_set__entity_object_id=entity.pk)
	m2m_q = Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__entity_content_type=entity_ct) & Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__entity_object_id=entity.pk)
	
	return Form.objects.filter(fk_q | m2m_q).distinct()


def get_view_forms(view, node):
	return get_entity_forms(view, passthrough=False) | get_entity_forms(node)