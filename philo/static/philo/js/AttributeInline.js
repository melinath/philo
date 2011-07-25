;(function($){
	var NS = 'attributes',
		VALUETYPE_ID_PATTERN = /id_philo-attribute-entity_content_type-entity_object_id-([0-9]+)-value_content_type/,
		attributesInline = {
		
		init: function () {
			var self = attributesInline,
				attributesWrapper = $('#philo-attribute-entity_content_type-entity_object_id-group'),
				valueTypeFields = $('select[name$="-value_content_type"]'),
				emptyForm = $('.empty-form', attributesWrapper),
				jsonTemplate = attributesInline.jsonTemplate = $('.row:nth-child(3)', emptyForm),
				foreignKeyTemplate = attributesInline.foreignKeyTemplate = $('.row:nth-child(4)', emptyForm),
				m2mTemplate = attributesInline.m2mTemplate = $('.row:nth-child(5)', emptyForm);
			
			// remove the fields from the template
			jsonTemplate.addClass('dynamic-fields').detach();
			foreignKeyTemplate.addClass('dynamic-fields').detach();
			m2mTemplate.addClass('dynamic-fields').detach();

			// bind the change event to all the valueTypeFields
			valueTypeFields.live('change.'+NS, self.valueTypeChangeHandler);
		},
		
		valueTypeChangeHandler: function (e) {
			var $this = $(this),
				attribute_number = $this.attr('id').match(VALUETYPE_ID_PATTERN)[1],
				value_type = $('option:selected', $this).text(),
				attributeWrapper = $this.closest('*[id^="philo-attribute-"]'),
				fieldset = $('fieldset', attributeWrapper);
			
			$('.dynamic-fields', fieldset).remove();
			
			switch (value_type){
				case 'json value':
					field_row = attributesInline.jsonTemplate.clone();
					break;
				case 'foreign key value':
					field_row = attributesInline.foreignKeyTemplate.clone();
					break;
				case 'many to many value':
					field_row = attributesInline.m2mTemplate.clone();
					break;
				default:
					field_row = '';
			}
			
			// replace __prefix__ with the index of the current attribute
			field_row.html(field_row.html().replace(/__prefix__/g, attribute_number));
			
			fieldset.append(field_row);
			
			// TODO: bind the foreign key events
		}
		
	}
	
	$(attributesInline.init);
}(django.jQuery));