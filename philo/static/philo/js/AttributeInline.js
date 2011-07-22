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
				value_type = $('option:selected', $this).text(),
				attributeWrapper = $this.closest('*[id^="philo-attribute-"]'),
				fieldset = $('fieldset', attributeWrapper);
			
			$('.dynamic-fields', fieldset).remove();
			
			if (value_type == 'json value') {
				fieldset.append(attributesInline.jsonTemplate.clone());
			} else if (value_type == 'foreign key value') {
				fieldset.append(attributesInline.foreignKeyTemplate.clone());
			} else if (value_type == 'many to many value') {
				fieldset.append(attributesInline.m2mTemplate.clone());
			}
		}
		
	}
	
	$(attributesInline.init);
}(django.jQuery));