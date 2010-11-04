from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from philo.contrib.bartleby.models import Form
from philo.models import Attribute, Entity


QUERYSET = 0
SET = 1


def get_entity_forms(entity, passthrough=True, return_value=QUERYSET):
	if return_value not in [QUERYSET, SET]:
		raise ValueError("Invalid return value type: %s" % return_value)
	
	if not isinstance(entity, Entity):
		raise TypeError
	
	if passthrough and entity.attributes.passthrough is not None:
		exclude_keys = [] # Exclude keys already found
		attribute_pks = set()
		
		def populate_attribute_pks(qs_mapper):
			for pk, key in qs_mapper.queryset.exclude(key__in=exclude_keys).values_list('pk', 'key'):
				attribute_pks.add(pk)
				exclude_keys.append(key)
			
			if qs_mapper.passthrough:
				populate_attribute_pks(qs_mapper.passthrough)
		
		populate_attribute_pks(entity.attributes)
		fk_q = Q(foreignkeyvalue_set__attribute_set__pk__in=attribute_pks)
		m2m_q = Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__pk__in=attribute_pks)
		form_pks = set(Form.objects.filter(fk_q | m2m_q).values_list('pk', flat=True).distinct())
		
		if return_value == QUERYSET:
			return Form.objects.filter(pk__in=form_pks)
		else:
			return form_pks
	
	entity_ct = ContentType.objects.get_for_model(entity)
	
	fk_q = Q(foreignkeyvalue_set__attribute_set__entity_content_type=entity_ct) & Q(foreignkeyvalue_set__attribute_set__entity_object_id=entity.pk)
	m2m_q = Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__entity_content_type=entity_ct) & Q(foreignkeyvalue_set__manytomanyvalue__attribute_set__entity_object_id=entity.pk)
	
	if return_value == QUERYSET:
		return Form.objects.filter(fk_q | m2m_q).distinct()
	else:
		return set(Form.objects.filter(fk_q | m2m_q).values_list('pk', flat=True))


def get_view_forms(view, node):
	# Until http://code.djangoproject.com/ticket/14609 is resolved, the following line will not work.
	#return get_entity_forms(view, passthrough=False) | get_entity_forms(node)
	# WORKAROUND - may actually be more efficient.
	form_pks = get_entity_forms(view, passthrough=False, return_value=SET)
	form_pks |= get_entity_forms(node, return_value=SET)
	return Form.objects.filter(pk__in=form_pks)
	# END WORKAROUND