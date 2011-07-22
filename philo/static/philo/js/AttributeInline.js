;(function($){
	var NS = 'attributes'
	var attributesInline = {
		
		init: function () {
			var self = attributesInline,
				attributesWrapper = $('#philo-attribute-entity_content_type-entity_object_id-group'),
				valueTypeFields = $('select[name$="-value_content_type"]'),
				emptyForm = $('.empty-form', attributesWrapper),
				jsonTemplate = attributesInline.jsonTemplate = $('.row:nth-child(3)', attributesWrapper),
				foreignKeyTemplate = attributesInline.foreignKeyTemplate = $('.row:nth-child(4)', attributesWrapper),
				m2mTemplate = attributesInline.m2mTemplate = $('.row:nth-child(5)', attributesWrapper);
			
			// remove the fields from the template
			jsonTemplate.addClass('dynamic-fields').detach();
			foreignKeyTemplate.addClass('dynamic-fields').detach();
			m2mTemplate.addClass('dynamic-fields').detach();
			// append an empty container
			$('fieldset', emptyForm).append('<div class="dynamic-attribute-container" />')
			
			// bind the change event to all the valueTypeFields
			valueTypeFields.live('change.'+NS, self.valueTypeChangeHandler);
		},
		
		valueTypeChangeHandler: function (e) {
			var $this = $(this),
				// TODO, figure out how to get the real attribute_number
				attribute_number = 0,
				value_type = $('option:selected', $this).text(),
				attributeWrapper = $this.closest('*[id^="philo-attribute-"]'),
				fieldset = $('fieldset', attributeWrapper);
			
			$('.dynamic-fields', fieldset).remove();
			
			switch (value_type){
				case 'json value':
					field_row = attributesInline.jsonTemplate;
					break;
				case 'foreign key value':
					field_row = attributesInline.foreignKeyTemplate;
					break;
				case 'many to many value':
					field_row = attributesInline.m2mTemplate;
					break;
				default:
					field_row = '';
			}
			
			// replace __prefix__ with the index of the current attribute
			field_row.html(field_row.html().replace(/__prefix__/g, attribute_number));
			console.log(field_row.html())
			
			fieldset.append(field_row);
			
			// TODO: bind the foreign key events
		}
		
	}
	
	$(attributesInline.init);
}(django.jQuery));