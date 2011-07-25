;(function($){
	var NS = 'attributes',
		VALUETYPE_ID_PATTERN = /id_philo-attribute-entity_content_type-entity_object_id-([0-9]+)-value_content_type/,
		JSON_ROW_SELECTOR = '.row:nth-child(3)',
		FK_ROW_SELECTOR = '.row:nth-child(4)',
		M2M_ROW_SELECTOR = '.row:nth-child(5)',
		attributesInline = {
		
		init: function () {
			var self = attributesInline,
				attributesWrapper = $('#philo-attribute-entity_content_type-entity_object_id-group'),
				valueTypeFields = $('select[name$="-value_content_type"]'),
				emptyForm = $('.empty-form', attributesWrapper),
				jsonTemplate = attributesInline.jsonTemplate = $('.row:nth-child(3)', emptyForm),
				foreignKeyTemplate = attributesInline.foreignKeyTemplate = $('.row:nth-child(4)', emptyForm),
				m2mTemplate = attributesInline.m2mTemplate = $('.row:nth-child(5)', emptyForm);

			// bind the change event to all the valueTypeFields
			valueTypeFields.live('change.'+NS, self.valueTypeChangeHandler);
		},
		
		valueTypeChangeHandler: function (e) {
			var $this = $(this),
				attribute_number = $this.attr('id').match(VALUETYPE_ID_PATTERN)[1],
				value_type = $('option:selected', $this).text(),
				attributeWrapper = $this.closest('*[id^="philo-attribute-"]'),
				fieldset = $('fieldset', attributeWrapper);
			
			$('.dynamic-fields', fieldset).hide();
			
			$([JSON_ROW_SELECTOR, FK_ROW_SELECTOR, M2M_ROW_SELECTOR].join(','), attributeWrapper).hide();
			
			switch (value_type){
				case 'json value':
					field_row = $(JSON_ROW_SELECTOR, attributeWrapper);
					break;
				case 'foreign key value':
					field_row = $(FK_ROW_SELECTOR, attributeWrapper);
					break;
				case 'many to many value':
					field_row = $(M2M_ROW_SELECTOR, attributeWrapper);
					break;
				default:
					field_row = '';
			}
			
			field_row.show();
		}
		
	}
	
	$(attributesInline.init);
}(django.jQuery));